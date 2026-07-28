export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    
    // Handle CORS
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        },
      });
    }

    // Route handling
    if (url.pathname === '/api/key-register' && request.method === 'POST') {
      return handleKeyRegister(request, env);
    }
    
    if (url.pathname === '/api/key-check' && request.method === 'GET') {
      return handleKeyCheck(request, env);
    }
    
    if (url.pathname === '/api/usage' && request.method === 'GET') {
      return handleUsage(request, env);
    }

    // Default response
    return new Response(JSON.stringify({ error: 'Not found' }), {
      status: 404,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};

async function handleKeyRegister(request, env) {
  try {
    const body = await request.json();
    const { userId, geminiKey } = body;
    
    if (!userId || !geminiKey) {
      return new Response(JSON.stringify({ error: 'Missing userId or geminiKey' }), {
        status: 400,
        headers: { 
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        },
      });
    }
    
    // Store in KV with timestamp
    const userData = {
      geminiKey,
      createdAt: Date.now(),
      usageCount: 0,
      lastUsed: Date.now(),
      dailyLimit: 50 // Default daily limit
    };
    
    await env.shen_user_db.put(`user:${userId}`, JSON.stringify(userData));
    
    return new Response(JSON.stringify({ 
      success: true, 
      message: 'API key registered successfully' 
    }), {
      headers: { 
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { 
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
    });
  }
}

async function handleKeyCheck(request, env) {
  try {
    const url = new URL(request.url);
    const userId = url.searchParams.get('userId');
    
    if (!userId) {
      return new Response(JSON.stringify({ error: 'Missing userId' }), {
        status: 400,
        headers: { 
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        },
      });
    }
    
    const userData = await env.shen_user_db.get(`user:${userId}`);
    
    if (!userData) {
      return new Response(JSON.stringify({ exists: false }), {
        headers: { 
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        },
      });
    }
    
    const parsed = JSON.parse(userData);
    
    // Check daily limit reset
    const now = Date.now();
    const lastReset = parsed.lastReset || 0;
    const dayInMs = 24 * 60 * 60 * 1000;
    
    if (now - lastReset > dayInMs) {
      parsed.usageCount = 0;
      parsed.lastReset = now;
      await env.shen_user_db.put(`user:${userId}`, JSON.stringify(parsed));
    }
    
    const canUse = parsed.usageCount < parsed.dailyLimit;
    
    return new Response(JSON.stringify({ 
      exists: true,
      canUse,
      usageCount: parsed.usageCount,
      dailyLimit: parsed.dailyLimit,
      remaining: parsed.dailyLimit - parsed.usageCount
    }), {
      headers: { 
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { 
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
    });
  }
}

async function handleUsage(request, env) {
  try {
    const url = new URL(request.url);
    const userId = url.searchParams.get('userId');
    
    if (!userId) {
      return new Response(JSON.stringify({ error: 'Missing userId' }), {
        status: 400,
        headers: { 
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        },
      });
    }
    
    const userData = await env.shen_user_db.get(`user:${userId}`);
    
    if (!userData) {
      return new Response(JSON.stringify({ error: 'User not found' }), {
        status: 404,
        headers: { 
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        },
      });
    }
    
    const parsed = JSON.parse(userData);
    
    // Increment usage
    parsed.usageCount += 1;
    parsed.lastUsed = Date.now();
    
    if (!parsed.lastReset) {
      parsed.lastReset = Date.now();
    }
    
    await env.shen_user_db.put(`user:${userId}`, JSON.stringify(parsed));
    
    const dayInMs = 24 * 60 * 60 * 1000;
    const now = Date.now();
    if (now - parsed.lastReset > dayInMs) {
      parsed.usageCount = 1;
      parsed.lastReset = now;
      await env.shen_user_db.put(`user:${userId}`, JSON.stringify(parsed));
    }
    
    return new Response(JSON.stringify({ 
      success: true,
      usageCount: parsed.usageCount,
      dailyLimit: parsed.dailyLimit,
      remaining: Math.max(0, parsed.dailyLimit - parsed.usageCount)
    }), {
      headers: { 
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { 
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
    });
  }
}
