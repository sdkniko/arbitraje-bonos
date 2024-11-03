// routes/bondAnalysis.js
const express = require('express');
const OpenAI = require('openai');
const axios = require('axios');
const router = express.Router();

// Configuración de OpenAI
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

// Función para obtener tweets y noticias relacionadas con un bono
async function getContentForBond(bondName) {
  // Simulamos obtener datos de diferentes fuentes
  const results = [];
  try {
    // Aquí irían las llamadas reales a las APIs
    results.push(`Ejemplo de contenido sobre ${bondName}`);
  } catch (error) {
    console.error(`Error fetching data for ${bondName}:`, error);
  }
  return results;
}

// Endpoint para analizar bonos
router.post('/analyze-bonds', async (req, res) => {
  try {
    const { bond1, bond2 } = req.body;

    if (!bond1 || !bond2) {
      return res.status(400).json({
        error: 'Se requieren los nombres de dos bonos para el análisis'
      });
    }

    // Obtener contenido para ambos bonos
    const [bond1Content, bond2Content] = await Promise.all([
      getContentForBond(bond1),
      getContentForBond(bond2)
    ]);

    // Crear el prompt para OpenAI
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

    // Obtener análisis de OpenAI
    const completion = await openai.chat.completions.create({
      messages: [
        { role: "system", content: "Eres un experto analista financiero especializado en bonos argentinos." },
        { role: "user", content: prompt }
      ],
      model: "gpt-4-turbo-preview",
      temperature: 0.7,
      max_tokens: 1000
    });

    // Procesar y enviar respuesta
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

module.exports = router;