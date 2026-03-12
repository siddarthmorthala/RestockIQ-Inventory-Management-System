import { useEffect, useMemo, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const initialSale = { item_id: '', quantity: 1 }
const initialShipment = { item_id: '', quantity: 1, sell_by_date: '' }

function App() {
  const [items, setItems] = useState([])
  const [suppliers, setSuppliers] = useState([])
  const [lowStock, setLowStock] = useState([])
  const [expiring, setExpiring] = useState([])
  const [reorder, setReorder] = useState([])
  const [sale, setSale] = useState(initialSale)
  const [shipment, setShipment] = useState(initialShipment)
  const [message, setMessage] = useState('')

  const loadData = async () => {
    const [itemsRes, suppliersRes, lowStockRes, expiringRes, reorderRes] = await Promise.all([
      fetch(`${API_URL}/items`),
      fetch(`${API_URL}/suppliers`),
      fetch(`${API_URL}/alerts/low-stock`),
      fetch(`${API_URL}/alerts/expiring`),
      fetch(`${API_URL}/reorder-suggestions`),
    ])

    const [itemsData, suppliersData, lowStockData, expiringData, reorderData] = await Promise.all([
      itemsRes.json(),
      suppliersRes.json(),
      lowStockRes.json(),
      expiringRes.json(),
      reorderRes.json(),
    ])

    setItems(itemsData)
    setSuppliers(suppliersData)
    setLowStock(lowStockData)
    setExpiring(expiringData)
    setReorder(reorderData)
    if (itemsData.length && !sale.item_id) {
      setSale({ ...initialSale, item_id: itemsData[0].id })
      setShipment({ ...initialShipment, item_id: itemsData[0].id })
    }
  }

  useEffect(() => { loadData() }, [])

  const inventoryByCategory = useMemo(() => {
    const buckets = {}
    for (const item of items) {
      buckets[item.category] = (buckets[item.category] || 0) + item.quantity_on_hand
    }
    return Object.entries(buckets).map(([category, quantity]) => ({ category, quantity }))
  }, [items])

  const submitAction = async (path, payload, successMessage) => {
    setMessage('')
    const res = await fetch(`${API_URL}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    const data = await res.json()
    if (!res.ok) {
      setMessage(data.detail || 'Something went wrong')
      return
    }
    setMessage(successMessage)
    await loadData()
  }

  return (
    <div className="page">
      <header className="hero">
        <div>
          <p className="eyebrow">RestockIQ • Angel's Liquor • Plano, TX</p>
          <h1>Inventory intelligence for a hometown liquor store</h1>
          <p>Replace spreadsheet tracking with live stock updates, reorder recommendations, FIFO expiration monitoring, and supplier visibility.</p>
        </div>
        <div className="pill">Docker + AWS ready</div>
      </header>

      {message && <div className="message">{message}</div>}

      <section className="grid two">
        <div className="card">
          <h2>On-hand inventory by category</h2>
          <div className="chartWrap">
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={inventoryByCategory}>
                <XAxis dataKey="category" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="quantity" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card stack">
          <div>
            <h2>Log sale</h2>
            <div className="formGrid">
              <select value={sale.item_id} onChange={(e) => setSale({ ...sale, item_id: Number(e.target.value) })}>
                {items.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
              </select>
              <input type="number" min="1" value={sale.quantity} onChange={(e) => setSale({ ...sale, quantity: Number(e.target.value) })} />
              <button onClick={() => submitAction('/sales', sale, 'Sale logged successfully')}>Submit sale</button>
            </div>
          </div>
          <div>
            <h2>Receive shipment</h2>
            <div className="formGrid">
              <select value={shipment.item_id} onChange={(e) => setShipment({ ...shipment, item_id: Number(e.target.value) })}>
                {items.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
              </select>
              <input type="number" min="1" value={shipment.quantity} onChange={(e) => setShipment({ ...shipment, quantity: Number(e.target.value) })} />
              <input type="date" value={shipment.sell_by_date} onChange={(e) => setShipment({ ...shipment, sell_by_date: e.target.value })} />
              <button onClick={() => submitAction('/shipments', { ...shipment, sell_by_date: shipment.sell_by_date || null }, 'Shipment received successfully')}>Receive shipment</button>
            </div>
          </div>
        </div>
      </section>

      <section className="grid three">
        <CardTable title="Low-stock alerts" rows={lowStock} columns={[
          ['Item', (row) => row.name], ['On hand', (row) => row.quantity_on_hand], ['Par', (row) => row.par_level]
        ]} emptyText="No low-stock alerts" />
        <CardTable title="Expiring soon" rows={expiring} columns={[
          ['Item', (row) => row.name], ['Qty', (row) => row.quantity_remaining], ['Days left', (row) => row.days_until_sell_by]
        ]} emptyText="No expiring lots" />
        <CardTable title="Reorder suggestions" rows={reorder} columns={[
          ['Item', (row) => row.name], ['Avg/day', (row) => row.seven_day_avg_sales], ['Order', (row) => row.suggested_reorder_qty]
        ]} emptyText="No reorder suggestions" />
      </section>

      <section className="grid two bottomGrid">
        <div className="card">
          <h2>Inventory</h2>
          <div className="tableWrap">
            <table>
              <thead>
                <tr><th>SKU</th><th>Name</th><th>Category</th><th>On hand</th><th>Par</th></tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.id}>
                    <td>{item.sku}</td>
                    <td>{item.name}</td>
                    <td>{item.category}</td>
                    <td>{item.quantity_on_hand}</td>
                    <td>{item.par_level}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <CardTable title="Supplier contacts" rows={suppliers} columns={[
          ['Supplier', (row) => row.name],
          ['Lead time', (row) => `${row.average_lead_time_days}d`],
          ['Contact', (row) => row.email],
        ]} emptyText="No suppliers loaded" />
      </section>
    </div>
  )
}

function CardTable({ title, rows, columns, emptyText }) {
  return (
    <div className="card">
      <h2>{title}</h2>
      {rows.length === 0 ? <p className="muted">{emptyText}</p> : (
        <div className="tableWrap compact">
          <table>
            <thead>
              <tr>{columns.map(([label]) => <th key={label}>{label}</th>)}</tr>
            </thead>
            <tbody>
              {rows.map((row, idx) => (
                <tr key={idx}>{columns.map(([label, render]) => <td key={label}>{render(row)}</td>)}</tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default App
