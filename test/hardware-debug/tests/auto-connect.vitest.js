import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useSerialStore } from '../src/stores/serial'

vi.mock('../src/api', () => ({
  api: {
    getPorts: vi.fn().mockResolvedValue([{ name: 'COM2' }]),
    connectSerial: vi.fn().mockResolvedValue({ success: true }),
    disconnectSerial: vi.fn().mockResolvedValue(null),
  }
}))

describe('serial store autoConnect', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('autoConnect sets portName to COM2 and starts connecting', async () => {
    const store = useSerialStore()

    expect(store.config.portName).toBe('COM1')
    expect(store.connecting).toBe(false)

    store.autoConnect('COM2')

    expect(store.config.portName).toBe('COM2')
    expect(store.connecting).toBe(true)
  })

  it('autoConnect ignores already-connected state', async () => {
    const store = useSerialStore()
    store.connected = true

    store.autoConnect('COM2')

    expect(store.config.portName).toBe('COM1')
    expect(store.connecting).toBe(false)
  })

  it('autoConnect ignores already-connecting state', async () => {
    const store = useSerialStore()
    store.connecting = true

    store.autoConnect('COM2')

    expect(store.config.portName).toBe('COM1')
  })
})
