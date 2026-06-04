import assert from 'assert/strict';

async function runTests() {
  let passed = 0;
  let failed = 0;

  console.log('\n=== Test: card tokens module should exist ===');
  try {
    const tokens = await import('../src/styles/card-tokens.js');
    assert.ok(tokens, 'card-tokens module should be importable');
    assert.ok(tokens.CARD_MIN_HEIGHT, 'CARD_MIN_HEIGHT should be defined');
    assert.ok(tokens.CARD_TITLE_FONT_SIZE, 'CARD_TITLE_FONT_SIZE should be defined');
    assert.ok(tokens.CARD_TITLE_FONT_WEIGHT, 'CARD_TITLE_FONT_WEIGHT should be defined');
    assert.ok(tokens.CARD_LABEL_FONT_SIZE, 'CARD_LABEL_FONT_SIZE should be defined');
    assert.ok(tokens.CARD_LABEL_FONT_WEIGHT, 'CARD_LABEL_FONT_WEIGHT should be defined');
    assert.ok(tokens.CARD_COUNT_FONT_SIZE, 'CARD_COUNT_FONT_SIZE should be defined');
    assert.ok(tokens.CARD_GRID_MIN_WIDTH, 'CARD_GRID_MIN_WIDTH should be defined');
    console.log('✓ PASS: card tokens module exists');
    passed++;
  } catch (err) {
    console.log(`✗ FAIL: ${err.message}`);
    failed++;
  }

  console.log('\n=== Test: card token values should match design spec ===');
  try {
    const tokens = await import('../src/styles/card-tokens.js');
    assert.strictEqual(tokens.CARD_MIN_HEIGHT, '220px', 'CARD_MIN_HEIGHT should be 220px');
    assert.strictEqual(tokens.CARD_TITLE_FONT_SIZE, '1.25rem', 'CARD_TITLE_FONT_SIZE should be 1.25rem');
    assert.strictEqual(tokens.CARD_TITLE_FONT_WEIGHT, '700', 'CARD_TITLE_FONT_WEIGHT should be 700');
    assert.strictEqual(tokens.CARD_LABEL_FONT_SIZE, '0.9375rem', 'CARD_LABEL_FONT_SIZE should be 0.9375rem');
    assert.strictEqual(tokens.CARD_LABEL_FONT_WEIGHT, '600', 'CARD_LABEL_FONT_WEIGHT should be 600');
    assert.strictEqual(tokens.CARD_COUNT_FONT_SIZE, '0.9375rem', 'CARD_COUNT_FONT_SIZE should be 0.9375rem');
    assert.strictEqual(tokens.CARD_GRID_MIN_WIDTH, '280px', 'CARD_GRID_MIN_WIDTH should be 280px');
    console.log('✓ PASS: all card token values match design spec');
    passed++;
  } catch (err) {
    console.log(`✗ FAIL: ${err.message}`);
    failed++;
  }

  console.log('\n=== Test: label font size should equal count font size (unified) ===');
  try {
    const tokens = await import('../src/styles/card-tokens.js');
    assert.strictEqual(
      tokens.CARD_LABEL_FONT_SIZE,
      tokens.CARD_COUNT_FONT_SIZE,
      'CARD_LABEL_FONT_SIZE and CARD_COUNT_FONT_SIZE should be equal'
    );
    console.log('✓ PASS: label and count font sizes are unified');
    passed++;
  } catch (err) {
    console.log(`✗ FAIL: ${err.message}`);
    failed++;
  }

  console.log('\n=== Test Results ===');
  console.log(`Passed: ${passed}`);
  console.log(`Failed: ${failed}`);

  if (failed > 0) {
    process.exit(1);
  }
}

runTests();