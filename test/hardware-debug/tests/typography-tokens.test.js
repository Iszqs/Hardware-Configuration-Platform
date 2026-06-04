import assert from 'assert/strict';

async function runTests() {
  let passed = 0;
  let failed = 0;

  // Test 1: typography-tokens module exists
  console.log('\n=== Test: typography tokens module should exist ===');
  try {
    const tokens = await import('../src/styles/typography-tokens.js');
    assert.ok(tokens, 'module should be importable');
    assert.ok(tokens.TEXT_XS, 'TEXT_XS should be defined');
    assert.ok(tokens.TEXT_SM, 'TEXT_SM should be defined');
    assert.ok(tokens.TEXT_BASE, 'TEXT_BASE should be defined');
    assert.ok(tokens.TEXT_MD, 'TEXT_MD should be defined');
    assert.ok(tokens.TEXT_LG, 'TEXT_LG should be defined');
    assert.ok(tokens.TEXT_XL, 'TEXT_XL should be defined');
    assert.ok(tokens.TEXT_2XL, 'TEXT_2XL should be defined');
    assert.ok(tokens.FW_NORMAL, 'FW_NORMAL should be defined');
    assert.ok(tokens.FW_MEDIUM, 'FW_MEDIUM should be defined');
    assert.ok(tokens.FW_SEMIBOLD, 'FW_SEMIBOLD should be defined');
    assert.ok(tokens.FW_BOLD, 'FW_BOLD should be defined');
    console.log('✓ PASS: all typography tokens are defined');
    passed++;
  } catch (err) {
    console.log(`✗ FAIL: ${err.message}`);
    failed++;
  }

  // Test 2: Token values match design spec
  console.log('\n=== Test: typography token values should match design spec ===');
  try {
    const tokens = await import('../src/styles/typography-tokens.js');
    assert.strictEqual(tokens.TEXT_XS, '0.75rem', 'TEXT_XS should be 0.75rem');
    assert.strictEqual(tokens.TEXT_SM, '0.875rem', 'TEXT_SM should be 0.875rem');
    assert.strictEqual(tokens.TEXT_BASE, '1rem', 'TEXT_BASE should be 1rem');
    assert.strictEqual(tokens.TEXT_MD, '1.125rem', 'TEXT_MD should be 1.125rem');
    assert.strictEqual(tokens.TEXT_LG, '1.25rem', 'TEXT_LG should be 1.25rem');
    assert.strictEqual(tokens.TEXT_XL, '1.5rem', 'TEXT_XL should be 1.5rem');
    assert.strictEqual(tokens.TEXT_2XL, '1.6rem', 'TEXT_2XL should be 1.6rem');
    assert.strictEqual(tokens.FW_NORMAL, '400', 'FW_NORMAL should be 400');
    assert.strictEqual(tokens.FW_MEDIUM, '500', 'FW_MEDIUM should be 500');
    assert.strictEqual(tokens.FW_SEMIBOLD, '600', 'FW_SEMIBOLD should be 600');
    assert.strictEqual(tokens.FW_BOLD, '700', 'FW_BOLD should be 700');
    console.log('✓ PASS: all typography token values match design spec');
    passed++;
  } catch (err) {
    console.log(`✗ FAIL: ${err.message}`);
    failed++;
  }

  // Test 3: No font-size value less than 0.75rem should exist in codebase
  console.log('\n=== Test: no font-size less than 0.75rem should be used ===');
  try {
    const tokens = await import('../src/styles/typography-tokens.js');
    const allValues = Object.values(tokens).filter(v => typeof v === 'string' && v.endsWith('rem'));
    for (const val of allValues) {
      const num = parseFloat(val);
      assert.ok(num >= 0.75, `Token value ${val} should not be less than 0.75rem`);
    }
    console.log('✓ PASS: all typography token values are >= 0.75rem');
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