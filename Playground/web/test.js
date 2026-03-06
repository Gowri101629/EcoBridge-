const GEMINI_API_KEY = "AIzaSyDQcBatdyZXCo4MA3s8fIeSncMN0M7kDQE";
async function test() {
  const systemPrompt = "You are a helpful assistant.";
  const question = "Hello";
  try {
    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${GEMINI_API_KEY}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        system_instruction: {
          parts: [{ text: systemPrompt }]
        },
        contents: [{
          parts: [{ text: question }]
        }]
      })
    });
    const result = await response.json();
    console.log("Success:", !!result.candidates);
  } catch (e) {
    console.error("Error!!!", e);
  }
}
test();
