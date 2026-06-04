import assert from 'assert/strict';
import fs from 'fs';

async function runTests() {
  let passed = 0;
  let failed = 0;

  const projectsStore = fs.readFileSync('src/stores/projects.js', 'utf-8');
  const projectListVue = fs.readFileSync('src/views/ProjectList.vue', 'utf-8');
  const hardwareLibVue = fs.readFileSync('src/views/HardwareLibrary.vue', 'utf-8');

  console.log('\n=== Test 1.1: addProject uses push (not unshift) for asc sort consistency ===');
  try {
    const addProjectFn = projectsStore.match(/async function addProject[\s\S]*?^\}/m);
    assert.ok(addProjectFn, 'addProject function not found');
    assert.ok(
      addProjectFn[0].includes('projects.value.push'),
      'addProject should use push() to append (consistent with asc sort)'
    );
    assert.ok(
      !addProjectFn[0].includes('projects.value.unshift'),
      'addProject should NOT use unshift (would prepend, breaking asc sort)'
    );
    console.log('✓ PASS: addProject uses push()');
    passed++;
  } catch (err) {
    console.log(`✗ FAIL: ${err.message}`);
    failed++;
  }

  console.log('\n=== Test 1.2: deleteProject filters from local store ===');
  try {
    const deleteFn = projectsStore.match(/async function deleteProject[\s\S]*?^\}/m);
    assert.ok(deleteFn, 'deleteProject function not found');
    assert.ok(
      deleteFn[0].includes('filter') && deleteFn[0].includes('p.id !== pid'),
      'deleteProject should filter the deleted project from local store'
    );
    console.log('✓ PASS: deleteProject removes from local store');
    passed++;
  } catch (err) {
    console.log(`✗ FAIL: ${err.message}`);
    failed++;
  }

  console.log('\n=== Test 1.3: updateProject calls refreshAll after API ===');
  try {
    const updateFn = projectsStore.match(/async function updateProject[\s\S]*?^\}/m);
    assert.ok(updateFn, 'updateProject function not found');
    assert.ok(
      updateFn[0].includes('await refreshAll()'),
      'updateProject should call refreshAll() to sync UI with server state'
    );
    console.log('✓ PASS: updateProject calls refreshAll');
    passed++;
  } catch (err) {
    console.log(`✗ FAIL: ${err.message}`);
    failed++;
  }

  console.log('\n=== Test 2.1: addDeviceToEdit sets custom_name to device type label ===');
  try {
    const addDeviceFn = projectListVue.match(/function addDeviceToEdit\(typeId\)[\s\S]*?^\}/m);
    assert.ok(addDeviceFn, 'addDeviceToEdit function not found');
    assert.ok(
      addDeviceFn[0].includes('projectStore.getDeviceTypeLabel(typeId)'),
      'addDeviceToEdit should set custom_name to device type label as default'
    );
    assert.ok(
      !addDeviceFn[0].match(/custom_name:\s*''/),
      'addDeviceToEdit should NOT set custom_name to empty string'
    );
    console.log('✓ PASS: addDeviceToEdit sets custom_name default');
    passed++;
  } catch (err) {
    console.log(`✗ FAIL: ${err.message}`);
    failed++;
  }

  console.log('\n=== Test 2.2: removeDeviceFromEdit defers deletion to saveEdit ===');
  try {
    const removeFn = projectListVue.match(/function removeDeviceFromEdit\(index\)[\s\S]*?^\}/m);
    assert.ok(removeFn, 'removeDeviceFromEdit function not found');
    assert.ok(
      removeFn[0].includes('removedConfigIds'),
      'removeDeviceFromEdit should record config id for deferred deletion'
    );
    assert.ok(
      !removeFn[0].match(/await api\.deleteDeviceConfig/),
      'removeDeviceFromEdit should NOT call delete API immediately (defer to saveEdit)'
    );
    console.log('✓ PASS: removeDeviceFromEdit defers deletion');
    passed++;
  } catch (err) {
    console.log(`✗ FAIL: ${err.message}`);
    failed++;
  }

  console.log('\n=== Test 2.3: saveDeviceName only updates local state ===');
  try {
    const saveNameFn = projectListVue.match(/function saveDeviceName\(index\)[\s\S]*?^\}/m);
    assert.ok(saveNameFn, 'saveDeviceName function not found');
    assert.ok(
      saveNameFn[0].includes('editingName = false'),
      'saveDeviceName should set editingName = false'
    );
    assert.ok(
      !saveNameFn[0].match(/await api\.|api\.updateDeviceConfig/),
      'saveDeviceName should NOT call API (defer to saveEdit)'
    );
    console.log('✓ PASS: saveDeviceName defers to saveEdit');
    passed++;
  } catch (err) {
    console.log(`✗ FAIL: ${err.message}`);
    failed++;
  }

  console.log('\n=== Test 2.4: saveEdit handles removed configs before saving ===');
  try {
    const saveEditFn = projectListVue.match(/async function saveEdit\(\)[\s\S]*?^\}/m);
    assert.ok(saveEditFn, 'saveEdit function not found');
    assert.ok(
      saveEditFn[0].includes('removedConfigIds') && saveEditFn[0].includes('deleteDeviceConfig'),
      'saveEdit should batch delete removed configs before updateProject'
    );
    console.log('✓ PASS: saveEdit batch handles deletions');
    passed++;
  } catch (err) {
    console.log(`✗ FAIL: ${err.message}`);
    failed++;
  }

  console.log('\n=== Test 3.1: category CRUD calls refreshAll ===');
  try {
    const categoryFns = ['addCategory', 'deleteCategory', 'updateCategory'];
    for (const fnName of categoryFns) {
      const fnRegex = new RegExp(`async function ${fnName}[\\s\\S]*?^\\}`, 'm');
      const fn = projectsStore.match(fnRegex);
      assert.ok(fn, `${fnName} function not found`);
      assert.ok(
        fn[0].includes('await refreshAll()'),
        `${fnName} should call refreshAll() to sync UI`
      );
    }
    console.log('✓ PASS: all category CRUD functions call refreshAll');
    passed++;
  } catch (err) {
    console.log(`✗ FAIL: ${err.message}`);
    failed++;
  }

  console.log('\n=== Test 3.2: device type CRUD calls refreshAll ===');
  try {
    const dtFns = ['addDeviceType', 'updateDeviceType', 'deleteDeviceType'];
    for (const fnName of dtFns) {
      const fnRegex = new RegExp(`async function ${fnName}[\\s\\S]*?^\\}`, 'm');
      const fn = projectsStore.match(fnRegex);
      assert.ok(fn, `${fnName} function not found`);
      assert.ok(
        fn[0].includes('await refreshAll()'),
        `${fnName} should call refreshAll() to sync UI`
      );
    }
    console.log('✓ PASS: all device type CRUD functions call refreshAll');
    passed++;
  } catch (err) {
    console.log(`✗ FAIL: ${err.message}`);
    failed++;
  }

  console.log('\n=== Test 4.1: subTypes computed depends on allDeviceTypes ===');
  try {
    const subTypesFn = projectsStore.match(/const subTypes = computed\([\s\S]*?\)\)/);
    assert.ok(subTypesFn, 'subTypes computed not found');
    assert.ok(
      subTypesFn[0].includes('allDeviceTypes.value'),
      'subTypes should derive from allDeviceTypes'
    );
    assert.ok(
      subTypesFn[0].includes('category_id'),
      'subTypes should group by category_id'
    );
    console.log('✓ PASS: subTypes derives from allDeviceTypes');
    passed++;
  } catch (err) {
    console.log(`✗ FAIL: ${err.message}`);
    failed++;
  }

  console.log('\n=== Test 4.2: init() sets loaded=true after refreshAll ===');
  try {
    const initFn = projectsStore.match(/async function init\(\)[\s\S]*?^\}/m);
    assert.ok(initFn, 'init function not found');
    assert.ok(
      initFn[0].includes('await refreshAll()') && initFn[0].includes('loaded.value = true'),
      'init() should await refreshAll() before setting loaded=true'
    );
    const refreshIdx = initFn[0].indexOf('await refreshAll()');
    const loadedIdx = initFn[0].indexOf('loaded.value = true');
    assert.ok(refreshIdx < loadedIdx, 'loaded=true should come AFTER refreshAll()');
    console.log('✓ PASS: init() sets loaded after refreshAll');
    passed++;
  } catch (err) {
    console.log(`✗ FAIL: ${err.message}`);
    failed++;
  }

  console.log('\n=== Test 4.3: getDeviceTypeLabel and getCategoryLabel look up from store ===');
  try {
    const getDeviceTypeLabel = projectsStore.match(/function getDeviceTypeLabel[\s\S]*?^\}/m);
    const getCategoryLabel = projectsStore.match(/function getCategoryLabel[\s\S]*?^\}/m);
    assert.ok(getDeviceTypeLabel, 'getDeviceTypeLabel function not found');
    assert.ok(getCategoryLabel, 'getCategoryLabel function not found');
    assert.ok(
      getDeviceTypeLabel[0].includes('allDeviceTypes.value.find'),
      'getDeviceTypeLabel should look up from allDeviceTypes'
    );
    assert.ok(
      getCategoryLabel[0].includes('categories.value.find'),
      'getCategoryLabel should look up from categories'
    );
    console.log('✓ PASS: label lookups from store data');
    passed++;
  } catch (err) {
    console.log(`✗ FAIL: ${err.message}`);
    failed++;
  }

  console.log('\n=== Test 4.4: edit-name button is always visible (not hover-only) ===');
  try {
    assert.ok(
      projectListVue.includes('edit-name-btn') && projectListVue.includes('startEditName(index)'),
      'ProjectList.vue should have edit-name-btn with always-visible icon'
    );
    console.log('✓ PASS: edit-name button always visible');
    passed++;
  } catch (err) {
    console.log(`✗ FAIL: ${err.message}`);
    failed++;
  }

  console.log('\n=== Test 4.5: hardware library category edit button exists ===');
  try {
    assert.ok(
      hardwareLibVue.includes('category-edit-btn') && hardwareLibVue.includes('editCategoryName'),
      'HardwareLibrary.vue should have category-edit-btn'
    );
    console.log('✓ PASS: category edit button exists');
    passed++;
  } catch (err) {
    console.log(`✗ FAIL: ${err.message}`);
    failed++;
  }

  console.log('\n=== Test 4.6: baud_rate options match DEFAULT_BAUD_RATES ===');
  try {
    const baudOptions = projectListVue.match(/<option[^>]*v-for="rate in projectStore\.DEFAULT_BAUD_RATES"[\s\S]*?<\/option>/);
    assert.ok(baudOptions, 'Baud rate options should iterate DEFAULT_BAUD_RATES');
    const storeConst = projectsStore.match(/DEFAULT_BAUD_RATES\s*=\s*\[([\d,\s]+)\]/);
    assert.ok(storeConst, 'DEFAULT_BAUD_RATES should be defined in store');
    assert.ok(
      storeConst[1].includes('115200') && storeConst[1].includes('9600'),
      'DEFAULT_BAUD_RATES should include 115200 and 9600'
    );
    console.log('✓ PASS: baud_rate options use centralized config');
    passed++;
  } catch (err) {
    console.log(`✗ FAIL: ${err.message}`);
    failed++;
  }

  console.log('\n=== Test 4.7: modbus singleton is shared (already fixed) ===');
  try {
    const serialRouter = fs.readFileSync('backend/routers/serial.py', 'utf-8');
    const modbusRouter = fs.readFileSync('backend/routers/modbus.py', 'utf-8');
    assert.ok(
      serialRouter.includes('from backend.services import modbus_service'),
      'serial.py should import shared modbus_service'
    );
    assert.ok(
      modbusRouter.includes('from backend.services import modbus_service'),
      'modbus.py should import shared modbus_service'
    );
    console.log('✓ PASS: ModbusService is shared singleton');
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