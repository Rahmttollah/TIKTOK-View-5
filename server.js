const express = require('express');
const crypto = require('crypto');
const https = require('https');
const { v4: uuidv4 } = require('uuid');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.static('public'));

// Safe Limits
const MAX_WORKERS = 2;
const SESSION_TIME = 30000;
const MIN_DELAY = 8000;
const MAX_DELAY = 15000;

// Global Storage
let tiktokIDs = [];
let videoQueue = [];
let activeCooldowns = {};
let systemStats = {
    totalViewsDelivered: 0,
    totalSessions: 0,
    activeWorkers: 0,
    queueLength: 0,
    systemStatus: '🟢 Running'
};

let isSystemRunning = true;

// 🚀 Device Generation
function generateAdvancedDevice() {
    const devices = ["SM-G973N", "SM-N975F", "SM-A715F", "Redmi Note 8", "OnePlus 8T"];
    const android_versions = ["9", "10", "11", "12"];
    const app_versions = ["160904", "170904", "180904"];
    
    const device_id = Array.from({length: 19}, () => '0123456789'[Math.floor(Math.random() * 10)]).join('');
    const iid = Array.from({length: 19}, () => '0123456789'[Math.floor(Math.random() * 10)]).join('');
    
    return {
        device_id: device_id,
        iid: iid,
        cdid: uuidv4(),
        openudid: Array.from({length: 16}, () => '0123456789abcdef'[Math.floor(Math.random() * 16)]).join(''),
        device_type: devices[Math.floor(Math.random() * devices.length)],
        os_version: android_versions[Math.floor(Math.random() * android_versions.length)],
        version_code: app_versions[Math.floor(Math.random() * app_versions.length)],
        device_brand: ["samsung", "xiaomi", "oneplus", "google"][Math.floor(Math.random() * 4)]
    };
}

// 🚀 Check Account Status
async function checkAccountStatus(tiktokID) {
    return new Promise((resolve) => {
        const options = {
            hostname: 'api16-va.tiktokv.com',
            port: 443,
            path: '/aweme/v1/user/profile/other/?',
            method: 'GET',
            headers: {
                'cookie': `sessionid=${tiktokID.session_id}`,
                'user-agent': 'TikTok 16.0.9 rv:160904 (Android 11; SM-G973N) Cronet',
                'x-gorgon': generateXGorgon(),
                'x-khronos': Math.floor(Date.now() / 1000).toString()
            },
            timeout: 5000
        };

        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', (chunk) => data += chunk);
            res.on('end', () => {
                try {
                    const jsonData = JSON.parse(data);
                    if (jsonData.status_code === 0) {
                        resolve({ success: true, status: '🟢 ACTIVE', username: tiktokID.username });
                    } else if (jsonData.status_code === 8) {
                        resolve({ success: false, status: '🔴 BANNED', error: 'Account banned' });
                    } else {
                        resolve({ success: false, status: '🟡 INVALID SESSION', error: 'Session expired' });
                    }
                } catch (e) {
                    resolve({ success: false, status: '🔴 ERROR', error: 'Check failed' });
                }
            });
        });

        req.on('error', () => resolve({ success: false, status: '🔴 NETWORK ERROR', error: 'Network issue' }));
        req.on('timeout', () => resolve({ success: false, status: '🟡 TIMEOUT', error: 'Request timeout' }));
        req.end();
    });
}

// 🚀 Add TikTok Session ID with Status Check
app.post('/add-session', async (req, res) => {
    const { username, session_id } = req.body;
    
    if (!username || !session_id) {
        return res.json({ success: false, message: 'Username and Session ID required', color: 'red' });
    }

    if (!session_id.match(/^[a-f0-9]{32}$/)) {
        return res.json({ success: false, message: 'Invalid Session ID format (32 character hex)', color: 'red' });
    }

    // Check if already exists
    if (tiktokIDs.find(id => id.username === username)) {
        return res.json({ success: false, message: 'Username already exists', color: 'orange' });
    }

    const newID = {
        username: username,
        session_id: session_id,
        device: generateAdvancedDevice(),
        isActive: true,
        lastUsed: null,
        totalViews: 0,
        successRate: 100,
        status: '🟡 Checking...',
        addedAt: new Date()
    };

    tiktokIDs.push(newID);

    // Check account status
    const statusResult = await checkAccountStatus(newID);
    newID.status = statusResult.status;
    newID.isActive = statusResult.success;

    if (statusResult.success) {
        res.json({ 
            success: true, 
            message: `✅ Account ${username} added and ACTIVE!`,
            color: 'green',
            totalIDs: tiktokIDs.length,
            status: statusResult.status
        });
    } else {
        res.json({ 
            success: false, 
            message: `❌ Account ${username} - ${statusResult.error}`,
            color: 'red',
            status: statusResult.status
        });
    }
});

// 🚀 Check All Accounts Status
app.get('/check-all-accounts', async (req, res) => {
    const results = [];
    
    for (const account of tiktokIDs) {
        const status = await checkAccountStatus(account);
        account.status = status.status;
        account.isActive = status.success;
        results.push({
            username: account.username,
            status: status.status,
            isActive: status.success
        });
    }
    
    res.json({ success: true, results: results });
});

// 🚀 Real View Request with Session ID
async function sendRealViewRequest(videoId, tiktokID) {
    return new Promise((resolve) => {
        if (!tiktokID.isActive) {
            resolve({ success: false, error: 'Account not active' });
            return;
        }

        const device = tiktokID.device;
        const endpoints = ['api16-va.tiktokv.com', 'api19-normal-c-useast1a.tiktokv.com'];
        const endpoint = endpoints[Math.floor(Math.random() * endpoints.length)];

        const params = new URLSearchParams({
            device_id: device.device_id,
            iid: device.iid,
            device_type: device.device_type,
            app_name: 'musically_go',
            host_abi: 'armeabi-v7a',
            channel: 'googleplay',
            device_platform: 'android',
            version_code: device.version_code,
            device_brand: device.device_brand,
            os_version: device.os_version,
            aid: '1340'
        }).toString();

        const payload = `item_id=${videoId}&play_delta=1`;
        const xGorgon = generateXGorgon();
        
        const options = {
            hostname: endpoint,
            port: 443,
            path: `/aweme/v1/aweme/stats/?${params}`,
            method: 'POST',
            headers: {
                'cookie': `sessionid=${tiktokID.session_id}`,
                'x-gorgon': xGorgon,
                'x-khronos': Math.floor(Date.now() / 1000).toString(),
                'user-agent': getRandomUserAgent(),
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'content-length': Buffer.byteLength(payload)
            },
            timeout: 8000
        };

        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', (chunk) => data += chunk);
            res.on('end', () => {
                try {
                    const jsonData = JSON.parse(data);
                    if (jsonData && jsonData.log_pb && jsonData.log_pb.impr_id) {
                        resolve({ success: true });
                    } else if (jsonData.status_code === 0) {
                        resolve({ success: true });
                    } else {
                        // Check if session is invalid
                        if (jsonData.status_code === 8) {
                            tiktokID.isActive = false;
                            tiktokID.status = '🔴 BANNED';
                        }
                        resolve({ success: false, error: 'Request rejected' });
                    }
                } catch (e) {
                    resolve({ success: false, error: 'Invalid response' });
                }
            });
        });

        req.on('error', () => resolve({ success: false, error: 'Network error' }));
        req.on('timeout', () => {
            req.destroy();
            resolve({ success: false, error: 'Timeout' });
        });

        req.write(payload);
        req.end();
    });
}

// 🚀 Get All TikTok IDs with Status
app.get('/get-ids', (req, res) => {
    const activeIDs = tiktokIDs.map(id => ({
        username: id.username,
        session_id: id.session_id.substring(0, 8) + '...',
        status: id.status,
        isActive: id.isActive,
        totalViews: id.totalViews,
        successRate: id.successRate.toFixed(1) + '%',
        lastUsed: id.lastUsed ? id.lastUsed.toLocaleTimeString() : 'Never'
    }));
    
    res.json({
        success: true,
        totalIDs: tiktokIDs.length,
        activeIDs: activeIDs,
        activeCount: tiktokIDs.filter(id => id.isActive).length,
        bannedCount: tiktokIDs.filter(id => id.status === '🔴 BANNED').length
    });
});

// 🚀 Delete TikTok ID
app.post('/delete-id', (req, res) => {
    const { username } = req.body;
    
    const initialLength = tiktokIDs.length;
    tiktokIDs = tiktokIDs.filter(id => id.username !== username);
    
    if (tiktokIDs.length < initialLength) {
        res.json({ success: true, message: `✅ ID ${username} deleted`, color: 'green' });
    } else {
        res.json({ success: false, message: '❌ ID not found', color: 'red' });
    }
});

// 🚀 Utility Functions
function generateXGorgon() {
    const base = '0404b0d30000';
    const random = Array.from({length: 24}, () => '0123456789abcdef'[Math.floor(Math.random() * 16)]).join('');
    return base + random;
}

function getRandomUserAgent() {
    const agents = [
        'okhttp/3.10.0.1',
        'TikTok 16.0.9 rv:160904 (Android 11; SM-G973N) Cronet'
    ];
    return agents[Math.floor(Math.random() * agents.length)];
}

// 🚀 Add Video to Queue
app.post('/add-video', (req, res) => {
    const { videoUrl, viewsCount = 500 } = req.body;
    
    if (!videoUrl) {
        return res.json({ success: false, message: '❌ Video URL required', color: 'red' });
    }

    const videoIdMatch = videoUrl.match(/\d{18,19}/g);
    if (!videoIdMatch) {
        return res.json({ success: false, message: '❌ Invalid TikTok URL', color: 'red' });
    }

    const videoId = videoIdMatch[0];
    
    if (activeCooldowns[videoId]) {
        const remaining = Math.ceil((activeCooldowns[videoId] - Date.now()) / 1000);
        return res.json({ 
            success: false, 
            message: `⏳ Video in cooldown. Try in ${remaining}s`,
            color: 'orange',
            cooldown: remaining
        });
    }

    const activeAccounts = tiktokIDs.filter(id => id.isActive).length;
    if (activeAccounts === 0) {
        return res.json({ 
            success: false, 
            message: '❌ No active TikTok accounts',
            color: 'red'
        });
    }

    const videoTask = {
        id: uuidv4(),
        videoUrl: videoUrl,
        videoId: videoId,
        viewsRequested: parseInt(viewsCount),
        viewsDelivered: 0,
        status: 'queued',
        addedAt: new Date()
    };

    videoQueue.push(videoTask);
    systemStats.queueLength = videoQueue.length;
    activeCooldowns[videoId] = Date.now() + 120000;

    res.json({ 
        success: true, 
        message: `✅ Video added! ${activeAccounts} active accounts working`,
        color: 'green',
        queuePosition: videoQueue.length,
        videoId: videoId,
        activeAccounts: activeAccounts
    });
});

// 🚀 Get System Status
app.get('/status', (req, res) => {
    const activeVideos = Object.keys(activeCooldowns).length;
    const activeAccounts = tiktokIDs.filter(id => id.isActive).length;
    const bannedAccounts = tiktokIDs.filter(id => id.status === '🔴 BANNED').length;
    
    res.json({
        system: systemStats,
        accounts: {
            total: tiktokIDs.length,
            active: activeAccounts,
            banned: bannedAccounts,
            working: systemStats.activeWorkers
        },
        storage: {
            queueLength: videoQueue.length,
            activeCooldowns: activeVideos
        },
        performance: {
            viewsPerMinute: calculateViewsPerMinute(),
            successRate: calculateSuccessRate() + '%',
            uptime: formatUptime(process.uptime())
        }
    });
});

// 🚀 Get Queue Status
app.get('/queue', (req, res) => {
    res.json({
        queue: videoQueue.map(task => ({
            videoId: task.videoId,
            requested: task.viewsRequested,
            delivered: task.viewsDelivered,
            progress: ((task.viewsDelivered / task.viewsRequested) * 100).toFixed(1) + '%',
            status: task.status
        })),
        activeCooldowns: Object.keys(activeCooldowns).map(videoId => ({
            videoId: videoId,
            cooldownEnds: new Date(activeCooldowns[videoId]).toLocaleTimeString()
        }))
    });
});

// 🚀 Safe Session Worker
async function startSafeSessionWorker(tiktokID) {
    console.log(`🚀 Starting: ${tiktokID.username} (${tiktokID.status})`);
    
    const sessionStart = Date.now();
    let viewsThisSession = 0;
    let successfulViews = 0;
    
    while (isSystemRunning && (Date.now() - sessionStart) < SESSION_TIME && tiktokID.isActive) {
        if (videoQueue.length === 0) {
            await new Promise(resolve => setTimeout(resolve, 3000));
            continue;
        }
        
        const videoTask = videoQueue[0];
        const result = await sendRealViewRequest(videoTask.videoId, tiktokID);
        
        viewsThisSession++;
        
        if (result.success) {
            successfulViews++;
            systemStats.totalViewsDelivered++;
            videoTask.viewsDelivered++;
            tiktokID.totalViews++;
            
            console.log(`✅ ${tiktokID.username} → ${videoTask.videoId}`);
            
            if (videoTask.viewsDelivered >= videoTask.viewsRequested) {
                videoQueue.shift();
                systemStats.queueLength = videoQueue.length;
                console.log(`🎉 COMPLETED: ${videoTask.videoId}`);
            }
        } else {
            console.log(`❌ ${tiktokID.username} failed: ${result.error}`);
            if (result.error.includes('BANNED')) {
                tiktokID.isActive = false;
                break;
            }
        }
        
        // Update success rate
        tiktokID.successRate = viewsThisSession > 0 ? (successfulViews / viewsThisSession) * 100 : 100;
        
        const delay = Math.random() * (MAX_DELAY - MIN_DELAY) + MIN_DELAY;
        await new Promise(resolve => setTimeout(resolve, delay));
    }
    
    console.log(`🛑 ${tiktokID.username} ended: ${successfulViews} views`);
    tiktokID.lastUsed = new Date();
    systemStats.activeWorkers--;
}

// 🚀 Main System Controller
async function startSafeSystem() {
    console.log('🚀 TikTok Session System Started');
    console.log('🔑 Using Session IDs for authentication');
    
    while (isSystemRunning) {
        // Clean expired cooldowns
        const now = Date.now();
        Object.keys(activeCooldowns).forEach(videoId => {
            if (activeCooldowns[videoId] < now) {
                delete activeCooldowns[videoId];
            }
        });
        
        // Start workers for active IDs
        const availableIDs = tiktokIDs.filter(id => id.isActive && systemStats.activeWorkers < MAX_WORKERS);
        
        for (const id of availableIDs) {
            if (systemStats.activeWorkers < MAX_WORKERS) {
                systemStats.activeWorkers++;
                systemStats.totalSessions++;
                
                startSafeSessionWorker(id).then(() => {
                    systemStats.activeWorkers--;
                });
                
                await new Promise(resolve => setTimeout(resolve, 10000));
            }
        }
        
        await new Promise(resolve => setTimeout(resolve, 15000));
    }
}

function calculateViewsPerMinute() {
    const uptimeMinutes = process.uptime() / 60;
    return uptimeMinutes > 0 ? (systemStats.totalViewsDelivered / uptimeMinutes).toFixed(1) : '0';
}

function calculateSuccessRate() {
    const totalAttempts = tiktokIDs.reduce((sum, id) => sum + id.totalViews, 0);
    const successfulViews = systemStats.totalViewsDelivered;
    return totalAttempts > 0 ? ((successfulViews / totalAttempts) * 100).toFixed(1) : 0;
}

function formatUptime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
}

// 🚀 Start Server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 TikTok Session System on port ${PORT}`);
    console.log(`🔑 Add Session IDs via /add-session`);
    startSafeSystem();
});
