export async function parseWebsite(url) {
    const response = await fetch("http://localhost:8000/api/v1/parse", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({url})
    });

    if (!response.ok) {
        throw new Error("Failed to parse recipe");
    }
    
    return response.json();
}