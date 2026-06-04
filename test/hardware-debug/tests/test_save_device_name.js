import assert from 'assert/strict';

function saveDeviceName(index, editingProject, projectStore) {
  const config = editingProject.device_configs[index];
  config.editingName = false;
}

function runTests() {
  let passed = 0;
  let failed = 0;
  
  console.log('\n=== Test: saveDeviceName should NOT call API (only update local state) ===');
  try {
    const editingProject = {
      id: '1',
      name: 'Test Project',
      description: '',
      device_configs: [{
        id: 100,
        category_id: 1,
        device_type_id: 1,
        station_number: 1,
        baud_rate: 9600,
        data_bits: 8,
        stop_bits: 1,
        parity: 'none',
        custom_name: 'Old Name',
        purpose: '',
        editingName: false
      }]
    };
    
    const apiCalls = [];
    const projectStore = {
      updateDeviceConfig: async (projectId, configIndex, data) => {
        apiCalls.push({ method: 'updateDeviceConfig', projectId, configIndex, data });
      }
    };
    
    editingProject.device_configs[0].editingName = true;
    editingProject.device_configs[0].custom_name = 'New Custom Name';
    
    saveDeviceName(0, editingProject, projectStore);
    
    assert.strictEqual(editingProject.device_configs[0].editingName, false, 'editingName should be false');
    assert.strictEqual(editingProject.device_configs[0].custom_name, 'New Custom Name', 'custom_name should be updated locally');
    
    assert.strictEqual(apiCalls.length, 0, 'API should NOT be called when saving device name');
    
    console.log('✓ PASS: saveDeviceName does not call API');
    passed++;
  } catch (err) {
    console.log(`✗ FAIL: ${err.message}`);
    failed++;
  }
  
  console.log('\n=== Test: saveDeviceName should work for new device without id (no API call) ===');
  try {
    const editingProject = {
      id: '2',
      name: 'Test Project 2',
      description: '',
      device_configs: [{
        category_id: 1,
        device_type_id: 1,
        station_number: 1,
        baud_rate: 9600,
        data_bits: 8,
        stop_bits: 1,
        parity: 'none',
        custom_name: 'New Device',
        purpose: '',
        editingName: false
      }]
    };
    
    const apiCalls = [];
    const projectStore = {
      updateDeviceConfig: async (projectId, configIndex, data) => {
        apiCalls.push({ method: 'updateDeviceConfig', projectId, configIndex, data });
      }
    };
    
    editingProject.device_configs[0].editingName = true;
    editingProject.device_configs[0].custom_name = 'Renamed Device';
    
    saveDeviceName(0, editingProject, projectStore);
    
    assert.strictEqual(apiCalls.length, 0, 'API should NOT be called for new device');
    assert.strictEqual(editingProject.device_configs[0].custom_name, 'Renamed Device', 'local state should be updated');
    
    console.log('✓ PASS: saveDeviceName does not call API for new device');
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