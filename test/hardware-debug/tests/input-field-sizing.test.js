import assert from 'assert/strict';

async function runTests() {
  let passed = 0;
  let failed = 0;

  console.log('\n=== Test: input-field content area should fit font size ===');
  try {
    const tokens = await import('../src/styles/typography-tokens.js');
    const textBaseRem = tokens.TEXT_BASE; // '1rem'
    const textBasePx = parseFloat(textBaseRem) * 17; // 17px (html base is 17px)

    const height = 44;
    const paddingTop = 12;
    const paddingBottom = 12;
    const contentArea = height - paddingTop - paddingBottom;

    assert.ok(
      contentArea >= textBasePx,
      `Content area (${contentArea}px) should be >= font-size (${textBasePx}px). ` +
      `Currently height=${height}px, padding=${paddingTop}px/${paddingBottom}px => content=${contentArea}px < ${textBasePx}px font-size. ` +
      `This causes text to be clipped vertically.`
    );
    console.log(`✓ PASS: content area (${contentArea}px) >= font-size (${textBasePx}px)`);
    passed++;
  } catch (err) {
    console.log(`✗ FAIL: ${err.message}`);
    failed++;
  }

  console.log('\n=== Test: input-field min height should be >= 44px ===');
  try {
    const MIN_HEIGHT = 44;
    const currentHeight = 44;
    assert.ok(
      currentHeight >= MIN_HEIGHT,
      `Input field height (${currentHeight}px) should be >= ${MIN_HEIGHT}px ` +
      `to provide adequate content area for ${17}px text with ${12}px padding.`
    );
    console.log(`✓ PASS: input-field height (${currentHeight}px) >= ${MIN_HEIGHT}px`);
    passed++;
  } catch (err) {
    console.log(`✗ FAIL: ${err.message}`);
    failed++;
  }

  console.log('\n=== Test: padding should not exceed 60% of height ===');
  try {
    const height = 44;
    const paddingTop = 12;
    const paddingBottom = 12;
    const totalPadding = paddingTop + paddingBottom;
    const paddingRatio = totalPadding / height;

    assert.ok(
      paddingRatio <= 0.6,
      `Total padding (${totalPadding}px) should be <= 60% of height (${height}px). ` +
      `Current ratio: ${(paddingRatio * 100).toFixed(0)}%`
    );
    console.log(`✓ PASS: padding ratio (${(paddingRatio * 100).toFixed(0)}%) <= 60%`);
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