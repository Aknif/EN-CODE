addEventListener('fetch', event => {
  event.respondWith(handleTestRequest(event.request))
})

async function handleTestRequest(request) {
  const serverUrl = 'http://YOUR_SERVER_IP:5000/test-connection'; // สร้าง endpoint นี้ใน app.py
  try {
    const response = await fetch(serverUrl);
    if (response.ok) {
      const text = await response.text();
      return new Response(`Server responded: ${text}`, { status: 200 });
    } else {
      return new Response(`Server error: ${response.status}`, { status: response.status });
    }
  } catch (error) {
    return new Response(`Fetch error: ${error.message}`, { status: 500 });
  }
}