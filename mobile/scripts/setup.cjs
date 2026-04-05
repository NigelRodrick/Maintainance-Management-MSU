/**
 * One-shot setup: npm install, cap add android (+ ios on macOS), cap sync.
 * Usage: node scripts/setup.cjs   or   npm run setup
 */
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');
process.chdir(root);

const run = (cmd, opts = {}) => {
  console.log(`\n> ${cmd}\n`);
  execSync(cmd, { stdio: 'inherit', env: { ...process.env, CI: 'true' }, ...opts });
};

if (!fs.existsSync(path.join(root, 'package.json'))) {
  console.error('Run from repo: mobile/');
  process.exit(1);
}

run('npm install');

const hasAndroid = fs.existsSync(path.join(root, 'android'));
const hasIos = fs.existsSync(path.join(root, 'ios'));

if (!hasAndroid) {
  run('npx cap add android');
} else {
  console.log('android/ already present — skipping cap add android');
}

if (process.platform === 'darwin') {
  if (!hasIos) {
    run('npx cap add ios');
  } else {
    console.log('ios/ already present — skipping cap add ios');
  }
} else {
  console.log('\n[iOS] Skipped: add the iOS project on macOS with: npx cap add ios\n');
}

run('npx cap sync');

console.log('\n--- Done ---');
console.log('Edit capacitor.config.json → server.url (HTTPS) before release builds.');
console.log('Android:  npm run open:android');
console.log('iOS (Mac): npm run open:ios\n');
