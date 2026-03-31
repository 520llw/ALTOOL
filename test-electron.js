/**
 * Electron 测试脚本
 * 用于验证 Electron 配置是否正确
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 检查 Electron 配置...\n');

let hasError = false;

// 检查必要文件
const requiredFiles = [
    'electron/main.js',
    'electron/preload.js',
    'package.json',
    'frontend/dist/index.html'
];

console.log('📁 检查必要文件:');
for (const file of requiredFiles) {
    const exists = fs.existsSync(path.join(__dirname, file));
    console.log(`  ${exists ? '✅' : '❌'} ${file}`);
    if (!exists) hasError = true;
}

// 检查 package.json 配置
console.log('\n📦 检查 package.json:');
try {
    const pkg = JSON.parse(fs.readFileSync(path.join(__dirname, 'package.json'), 'utf8'));
    
    console.log(`  ✅ name: ${pkg.name}`);
    console.log(`  ✅ version: ${pkg.version}`);
    console.log(`  ✅ main: ${pkg.main}`);
    
    if (pkg.scripts && pkg.scripts['electron:start']) {
        console.log(`  ✅ electron:start script exists`);
    } else {
        console.log(`  ❌ electron:start script missing`);
        hasError = true;
    }
    
    if (pkg.build) {
        console.log(`  ✅ electron-builder config exists`);
        console.log(`    - appId: ${pkg.build.appId}`);
        console.log(`    - productName: ${pkg.build.productName}`);
    } else {
        console.log(`  ❌ electron-builder config missing`);
        hasError = true;
    }
} catch (error) {
    console.log(`  ❌ Error reading package.json: ${error.message}`);
    hasError = true;
}

// 检查前端构建
console.log('\n🔨 检查前端构建:');
const frontendDist = path.join(__dirname, 'frontend', 'dist');
if (fs.existsSync(frontendDist)) {
    const files = fs.readdirSync(frontendDist);
    console.log(`  ✅ frontend/dist exists (${files.length} items)`);
    
    const indexHtml = path.join(frontendDist, 'index.html');
    if (fs.existsSync(indexHtml)) {
        console.log(`  ✅ index.html exists`);
    } else {
        console.log(`  ❌ index.html missing`);
        hasError = true;
    }
    
    const assetsDir = path.join(frontendDist, 'assets');
    if (fs.existsSync(assetsDir)) {
        const assets = fs.readdirSync(assetsDir);
        console.log(`  ✅ assets directory exists (${assets.length} files)`);
    } else {
        console.log(`  ❌ assets directory missing`);
        hasError = true;
    }
} else {
    console.log(`  ❌ frontend/dist not found - run: cd frontend && npm run build`);
    hasError = true;
}

// 检查后端
console.log('\n🐍 检查后端:');
const backendDir = path.join(__dirname, 'backend');
if (fs.existsSync(backendDir)) {
    const appMain = path.join(backendDir, 'app', 'main.py');
    if (fs.existsSync(appMain)) {
        console.log(`  ✅ backend/app/main.py exists`);
    } else {
        console.log(`  ❌ backend/app/main.py missing`);
        hasError = true;
    }
    
    // 检查虚拟环境
    const venvDir = path.join(backendDir, 'venv');
    if (fs.existsSync(venvDir)) {
        console.log(`  ✅ backend/venv exists`);
    } else {
        console.log(`  ⚠️  backend/venv not found (optional but recommended)`);
    }
} else {
    console.log(`  ❌ backend directory missing`);
    hasError = true;
}

// 总结
console.log('\n' + '='.repeat(50));
if (hasError) {
    console.log('❌ 检查失败，请修复上述问题后再试。');
    process.exit(1);
} else {
    console.log('✅ 所有检查通过！');
    console.log('\n🚀 启动命令:');
    console.log('   npm run electron:start    - 启动 Electron (生产模式)');
    console.log('   npm run electron:dev      - 启动 Electron (开发模式)');
    console.log('   npm run electron:build    - 打包应用');
}
