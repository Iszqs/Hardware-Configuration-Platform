import assert from 'assert/strict';

function addDeviceToEdit(typeId, projectStore, editingProject) {
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
    custom_name: projectStore.getDeviceTypeLabel ? projectStore.getDeviceTypeLabel(typeId) : '',
    purpose: ''
  });
}

async function updateProject(projectId, data, api) {
  await api.updateProject(projectId, {
    name: data.name,
    description: data.description
  });
  
  if (data.device_configs && Array.isArray(data.device_configs)) {
    for (const config of data.device_configs) {
      if (config.id) {
        await api.updateDeviceConfig(config.id, {
          station_number: config.station_number,
          baud_rate: config.baud_rate,
          data_bits: config.data_bits,
          stop_bits: config.stop_bits,
          parity: config.parity,
          custom_name: config.custom_name,
          purpose: config.purpose
        });
      } else {
        await api.addDeviceConfig(projectId, {
          category_id: config.category_id,
          device_type_id: config.device_type_id,
          station_number: config.station_number,
          baud_rate: config.baud_rate,
          data_bits: config.data_bits,
          stop_bits: config.stop_bits,
          parity: config.parity,
          custom_name: config.custom_name,
          purpose: config.purpose
        });
      }
    }
  }
}

async function runTests() {
  let passed = 0;
  let failed = 0;
  
  console.log('\n=== Test: custom_name should be preserved during save ===');
  try {
    const projectStore = { getCategoryByType: () => 1, getDeviceTypeLabel: (id) => ({ 1: '35电机', 2: '57电机' }[id] || '') };
    const editingProject = {
      id: '1',
      name: 'Test Project',
      description: '',
      device_configs: []
    };
    
    addDeviceToEdit(1, projectStore, editingProject);
    
    editingProject.device_configs[0].custom_name = 'My Custom Device';
    
    const apiCalls = [];
    const mockApi = {
      updateProject: async (id, data) => apiCalls.push({ method: 'updateProject', id, data }),
      addDeviceConfig: async (pid, data) => apiCalls.push({ method: 'addDeviceConfig', pid, data }),
      updateDeviceConfig: async (cid, data) => apiCalls.push({ method: 'updateDeviceConfig', cid, data })
    };
    
    await updateProject(1, {
      name: editingProject.name,
      description: editingProject.description,
      device_configs: JSON.parse(JSON.stringify(editingProject.device_configs))
    }, mockApi);
    
    const addCall = apiCalls.find(c => c.method === 'addDeviceConfig');
    assert.ok(addCall, 'addDeviceConfig should be called');
    assert.ok('custom_name' in addCall.data, 'custom_name should be in API call data');
    assert.strictEqual(addCall.data.custom_name, 'My Custom Device', 'custom_name should have the edited value');
    
    console.log('✓ PASS: custom_name is preserved during save');
    passed++;
  } catch (err) {
    console.log(`✗ FAIL: ${err.message}`);
    failed++;
  }
  
  console.log('\n=== Test: custom_name should default to device type label when not edited ===');
  try {
    const projectStore = { getCategoryByType: () => 1, getDeviceTypeLabel: (id) => ({ 1: '35电机', 2: '57电机' }[id] || '') };
    const editingProject = {
      id: '2',
      name: 'Test Project 2',
      description: '',
      device_configs: []
    };
    
    addDeviceToEdit(2, projectStore, editingProject);
    
    const apiCalls = [];
    const mockApi = {
      updateProject: async (id, data) => apiCalls.push({ method: 'updateProject', id, data }),
      addDeviceConfig: async (pid, data) => apiCalls.push({ method: 'addDeviceConfig', pid, data }),
      updateDeviceConfig: async (cid, data) => apiCalls.push({ method: 'updateDeviceConfig', cid, data })
    };
    
    await updateProject(2, {
      name: editingProject.name,
      description: editingProject.description,
      device_configs: JSON.parse(JSON.stringify(editingProject.device_configs))
    }, mockApi);
    
    const addCall = apiCalls.find(c => c.method === 'addDeviceConfig');
    assert.ok(addCall, 'addDeviceConfig should be called');
    assert.strictEqual(addCall.data.custom_name, '57电机', 'custom_name should default to device type label when not edited');
    
    console.log('✓ PASS: custom_name defaults to device type label when not edited');
    passed++;
  } catch (err) {
    console.log(`✗ FAIL: ${err.message}`);
    failed++;
  }
  
  console.log('\n=== Test: existing device custom_name should be updated ===');
  try {
    const apiCalls = [];
    const mockApi = {
      updateProject: async (id, data) => apiCalls.push({ method: 'updateProject', id, data }),
      addDeviceConfig: async (pid, data) => apiCalls.push({ method: 'addDeviceConfig', pid, data }),
      updateDeviceConfig: async (cid, data) => apiCalls.push({ method: 'updateDeviceConfig', cid, data })
    };
    
    await updateProject(3, {
      name: 'Test Project 3',
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
        custom_name: 'Updated Name',
        purpose: ''
      }]
    }, mockApi);
    
    const updateCall = apiCalls.find(c => c.method === 'updateDeviceConfig');
    assert.ok(updateCall, 'updateDeviceConfig should be called');
    assert.strictEqual(updateCall.data.custom_name, 'Updated Name', 'custom_name should be updated');
    
    console.log('✓ PASS: existing device custom_name is updated correctly');
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