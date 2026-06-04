const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');

const app = express();
const PORT = process.env.PORT || 5175;

app.use(cors());

const distPaths = [
  path.join(__dirname, 'dist'),
  path.join(process.cwd(), 'dist'),
  path.join(path.dirname(process.execPath), 'dist')
];

let distPath = null;
for (const p of distPaths) {
  if (fs.existsSync(p)) {
    distPath = p;
    break;
  }
}

if (distPath) {
  app.use(express.static(distPath));
  console.log('静态资源目录:', distPath);
} else {
  console.log('[警告] 未找到 dist 目录');
}

app.get('/', (req, res) => {
  if (distPath) {
    res.sendFile(path.join(distPath, 'index.html'));
  } else {
    res.status(500).send('静态资源目录未找到');
  }
});

app.listen(PORT, () => {
  console.log('═══════════════════════════════════════');
  console.log('   硬件配置平台服务已启动');
  console.log('═══════════════════════════════════════');
  console.log('');
  console.log(`   请在浏览器中访问:`);
  console.log(`   http://localhost:${PORT}`);
  console.log('');
  console.log('   按 Ctrl+C 停止服务');
  console.log('═══════════════════════════════════════');
  
  const startCmd = process.platform === 'win32' 
    ? `start http://localhost:${PORT}`
    : `open http://localhost:${PORT}`;
  
  exec(startCmd, (err) => {
    if (err) {
      console.log('');
      console.log('请手动打开浏览器访问: http://localhost:' + PORT);
    }
  });
});
