// Importar módulos necesarios
const express = require('express');
const { spawn } = require('child_process');
const mongoose = require('mongoose');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const speakeasy = require('speakeasy');
const qrcode = require('qrcode');
const qrcodeterminal = require('qrcode-terminal');
const OpenAI = require('openai');
const axios = require('axios');
require('dotenv').config();

// Crear una instancia de Express
const app = express();
const PORT = 3000;
const JWT_SECRET = 'secreto_super_seguro';

// Configuración de OpenAI
const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY
});

// Conectar a la base de datos de MongoDB
mongoose.connect('mongodb://localhost:27017/tu_base_de_datos', {
    useNewUrlParser: true,
    useUnifiedTopology: true
});

// Middleware para parsear JSON en las solicitudes
app.use(express.json());

// Modelo de usuario con campo de secreto TOTP
const userSchema = new mongoose.Schema({
    username: { type: String, required: true, unique: true },
    password: { type: String, required: true },
    totpSecret: { type: String }
});

const User = mongoose.model('User', userSchema);

// Middleware para verificar el token JWT
const authenticateToken = (req, res, next) => {
    const token = req.headers['authorization'];
    if (!token) return res.status(403).json({ message: 'Token requerido' });

    jwt.verify(token.split(" ")[1], JWT_SECRET, (err, user) => {
        if (err) return res.status(403).json({ message: 'Token inválido' });
        req.user = user;
        next();
    });
};

// Middleware para verificar el TOTP
const verifyTOTP = async (req, res, next) => {
    const { totp } = req.headers;
    if (!totp) return res.status(403).json({ message: 'TOTP requerido' });

    const user = await User.findOne({ username: req.user.username });
    if (!user || !user.totpSecret) return res.status(403).json({ message: 'TOTP no configurado' });

    const isValidTOTP = speakeasy.totp.verify({
        secret: user.totpSecret,
        encoding: 'base32',
        token: totp
    });

    if (!isValidTOTP) {
        return res.status(403).json({ message: 'TOTP inválido' });
    }
    next();
};

// Endpoint de registro
app.post('/register', async (req, res) => {
    const { username, password } = req.body;
    const hashedPassword = await bcrypt.hash(password, 10);

    try {
        const newUser = new User({ username, password: hashedPassword });
        await newUser.save();
        res.status(201).json({ message: 'Usuario registrado exitosamente' });
    } catch (error) {
        res.status(400).json({ message: 'Error al registrar el usuario', error });
    }
});

// Endpoint de login
app.post('/login', async (req, res) => {
    const { username, password } = req.body;
    const user = await User.findOne({ username });

    if (!user || !await bcrypt.compare(password, user.password)) {
        return res.status(403).json({ message: 'Credenciales incorrectas' });
    }

    const token = jwt.sign({ username: user.username }, JWT_SECRET, { expiresIn: '1h' });

    if (!user.totpSecret) {
        const secret = speakeasy.generateSecret({ length: 20 });
        user.totpSecret = secret.base32;
        await user.save();

        // Crear la URL para el código QR
        const otpauthUrl = speakeasy.otpauthURL({
            secret: secret.base32,
            label: encodeURIComponent(username),
            issuer: encodeURIComponent('empresa'),
            encoding: 'base32'
        });

        // Generar la imagen QR y convertirla a URL de datos
        qrcode.toDataURL(otpauthUrl)
            .then(dataUrl => {
                res.json({
                    message: 'Login exitoso',
                    token,
                    totpSecret: secret.base32,
                    qrCode: dataUrl // Aquí está la URL de la imagen QR
                });
            })
            .catch(err => {
                console.error('Error generando QR:', err);
                res.status(500).json({ message: 'Error generando QR para TOTP' });
            });
    } else {
        // Si el usuario ya tiene TOTP configurado, solo devolver el token
        res.json({
            message: 'Login exitoso',
            token
        });
    }
});

// Función auxiliar para obtener contenido de bonos
async function getContentForBond(bondName) {
    const results = [];
    try {
        results.push(`Ejemplo de contenido sobre ${bondName}`);
    } catch (error) {
        console.error(`Error fetching data for ${bondName}:`, error);
    }
    return results;
}

// Endpoint para análisis de bonos (con autenticación y TOTP)
app.post('/api/analyze-bonds', authenticateToken, verifyTOTP, async (req, res) => {
    try {
        const { bond1, bond2 } = req.body;

        if (!bond1 || !bond2) {
            return res.status(400).json({
                error: 'Se requieren los nombres de dos bonos para el análisis'
            });
        }

        const [bond1Content, bond2Content] = await Promise.all([
            getContentForBond(bond1),
            getContentForBond(bond2)
        ]);

        const prompt = `
        Analiza el siguiente contenido de redes sociales y fuentes financieras sobre dos bonos argentinos y proporciona una recomendación de inversión:

        Bono 1: ${bond1}
        Contenido relacionado:
        ${bond1Content.join('\n')}

        Bono 2: ${bond2}
        Contenido relacionado:
        ${bond2Content.join('\n')}

        Por favor, proporciona:
        1. Un análisis de sentimiento general para cada bono
        2. Principales factores que influyen en cada bono
        3. Una recomendación clara sobre cuál bono comprar y por qué
        4. Nivel de riesgo asociado
        `;

        const completion = await openai.chat.completions.create({
            messages: [
                { role: "system", content: "Eres un experto analista financiero especializado en bonos argentinos." },
                { role: "user", content: prompt }
            ],
            model: "gpt-4-turbo-preview",
            temperature: 0.7,
            max_tokens: 1000
        });

        const analysis = completion.choices[0].message.content;

        return res.json({
            recommendation: analysis,
            analyzedBonds: {
                bond1,
                bond2
            },
            timestamp: new Date(),
            disclaimer: "Este análisis es generado por IA y no constituye asesoramiento financiero profesional."
        });

    } catch (error) {
        console.error('Error en el análisis de bonos:', error);
        return res.status(500).json({
            error: 'Error al procesar la solicitud',
            details: error.message
        });
    }
});

// Endpoint para inicializar el script de Python
app.post('/ejecutar-python', authenticateToken, verifyTOTP, (req, res) => {
    const { simbolo, fecha_desde, fecha_hasta } = req.body;

    const pythonProcess = spawn('python', ['main.py'], {
        env: { ...process.env, SIMBOLO: simbolo, FECHA_DESDE: fecha_desde, FECHA_HASTA: fecha_hasta }
    });

    let pythonOutput = '';
    pythonProcess.stdout.on('data', (data) => {
        pythonOutput += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Error: ${data}`);
    });

    pythonProcess.on('close', (code) => {
        if (code === 0) {
            res.status(200).send({ message: 'Script ejecutado correctamente', output: pythonOutput });
        } else {
            res.status(500).send({ message: 'Error al ejecutar el script de Python' });
        }
    });
});

// Endpoint para ejecutar el script de Python 'grafico.py'
app.post('/generar-grafico', authenticateToken, verifyTOTP, (req, res) => {
    const { simbolo1, simbolo2, fecha_desde, fecha_hasta } = req.body;

    const pythonProcess = spawn('python', ['grafico.py'], {
        env: { 
            ...process.env, 
            SIMBOLO1: simbolo1, 
            SIMBOLO2: simbolo2, 
            FECHA_DESDE: fecha_desde, 
            FECHA_HASTA: fecha_hasta 
        }
    });

    let pythonOutput = '';
    pythonProcess.stdout.on('data', (data) => {
        pythonOutput += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Error: ${data}`);
        res.status(500).send({ message: 'Error al ejecutar el script de Python', error: data.toString() });
    });

    pythonProcess.on('close', (code) => {
        if (code === 0) {
            res.status(200).send({ message: 'Script ejecutado correctamente', output: pythonOutput });
        } else {
            res.status(500).send({ message: 'Error al ejecutar el script de Python' });
        }
    });
});

// Iniciar el servidor
app.listen(PORT, () => {
    console.log(`Servidor escuchando en http://localhost:${PORT}`);
});