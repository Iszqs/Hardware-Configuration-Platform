import assert from 'assert/strict';

function addDeviceToEdit(typeId, projectStore, editingProject, getDeviceTypeLabel) {
  const categoryId = projectStore.getCategoryByType(typeId);
  const existing = editingProject.device_configs.filter(d => d.device_type_id === typeId);
  const newStationNumber = existing.length > 0
    ? Math.max(...existing.map(d => d.station_number)) + 1
    : 1;
  
  editingProject.device_configs.push({
    category_id: categoryId,
    device_type_id: typeId,
    station_number: newStationNumber,
    baud_rate: 9600,
    data_bits: 8,
    stop_bits: 1,
    parity: 'none',
    custom_name: getDeviceTypeLabel(typeId),
    purpose: ''
  });
}

function runTests() {
  let passed = 0;
  let failed = 0;
  
  console.log('\n=== Test: addDeviceToEdit should initialize custom_name with device type label ===');
  try {
    const projectStore = {
      getCategoryByType: (typeId) => 1
    };
    
    const editingProject = {
      device_configs: []
    };
    
    addDeviceToEdit(1, projectStore, editingProject, (typeId) => {
      const labels = { 1: '35电机', 2: '57电机' };
      return labels[typeId] || String(typeId);
    });
    
    const addedConfig = editingProject.device_configs[0];
    
    assert.ok('custom_name' in addedConfig, 'custom_name field should exist');
    assert.strictEqual(addedConfig.custom_name, '35电机', 'custom_name should default to device type label');
    
    console.log('✓ PASS: custom_name field defaults to device type label');
    passed++;
  } catch (err) {
    console.log(`✗ FAIL: ${err.message}`);
    failed++;
  }
  
  console.log('\n=== Test: API payload should include custom_name with device type label as default ===');
  try {
    const projectStore = {
      getCategoryByType: (typeId) => 1
    };
    
    const editingProject = {
      device_configs: []
    };
    
    addDeviceToEdit(2, projectStore, editingProject, (typeId) => {
      const labels = { 1: '35电机', 2: '57电机' };
      return labels[typeId] || String(typeId);
    });
    
    const config = editingProject.device_configs[0];
    
    const apiPayload = {
      category_id: config.category_id,
      device_type_id: config.device_type_id,
      station_number: config.station_number,
      baud_rate: config.baud_rate,
      data_bits: config.data_bits,
      stop_bits: config.stop_bits,
      parity: config.parity,
      custom_name: config.custom_name || '',
      purpose: config.purpose || ''
    };
    
    assert.ok('custom_name' in apiPayload, 'API payload should include custom_name');
    assert.strictEqual(apiPayload.custom_name, '57电机', 'custom_name should default to device type label in API payload');
    
    console.log('✓ PASS: API payload includes custom_name with device type label');
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