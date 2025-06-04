export const loginAndGetToken = async (): Promise<string> => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);
  
      const response = await fetch('http://127.0.0.1:5000/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: 'admin',
          password: 'securepass',
        }),
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
  
      console.log('Login request:', { method: 'POST', url: 'http://127.0.0.1:5000/login', headers: response.headers });
      console.log('Login response:', response.status, await response.text());
      if (!response.ok) throw new Error(`Login failed: ${response.status} - ${await response.text()}`);
      const data = await response.json();
      localStorage.setItem('token', data.access_token);
      return data.access_token;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };