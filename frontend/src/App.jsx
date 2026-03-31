import React, { useState } from "react";
import axios from "axios";
import jsPDF from "jspdf";
import {
LineChart,
Line,
XAxis,
YAxis,
CartesianGrid,
Tooltip,
ResponsiveContainer
} from "recharts";
import "./App.css";

function App() {

const [ticker, setTicker] = useState("");
const [data, setData] = useState(null);
const [loading, setLoading] = useState(false);
const [chartData, setChartData] = useState([]);

const analyzeStock = async () => {

if (!ticker) {
alert("Please enter stock ticker");
return;
}

try {

setLoading(true);

const response = await axios.get(
`http://127.0.0.1:8000/analyze/${ticker}`
);

setData(response.data);

/* Get real chart data from backend */
setChartData(response.data.chart || []);

setLoading(false);

} catch (error) {

console.error(error);
alert("Error connecting to backend");
setLoading(false);

}

};
/*Download <pdf></pdf>*/
const downloadPDF = () => {

  const doc = new jsPDF();

  doc.text("AI Financial Report", 10, 10);

  doc.text(`Ticker: ${data.ticker}`, 10, 20);
  doc.text(`Price: ${data.price}`, 10, 30);

  doc.text("Report:", 10, 40);

  doc.text(data.report, 10, 50);

  doc.save(`${data.ticker}_report.pdf`);
};
return (

<div className="container">

<header className="header">

<h1>AI Financial Intelligence Platform</h1>

<p>
AI powered stock analysis, sentiment detection and market intelligence
</p>

</header>

<div className="searchBox">

<input
type="text"
placeholder="Search Stock (AAPL, TSLA, MSFT)"
value={ticker}
onChange={(e) => setTicker(e.target.value)}
onKeyDown={(e) => {
  if (e.key === "Enter") {
    analyzeStock();
  }
}}
/>

<button onClick={analyzeStock}>
{loading ? "Analyzing..." : "Analyze"}
</button>

</div>

{/* Welcome section */}

{!data && (

<div className="welcome">

<div className="infoCard">
<h3>📈 Market Analysis</h3>
<p>Analyze stock performance and financial metrics instantly.</p>
</div>

<div className="infoCard">
<h3>📰 News Intelligence</h3>
<p>AI reads news and detects positive or negative sentiment.</p>
</div>

<div className="infoCard">
<h3>🤖 AI Insights</h3>
<p>Get AI generated summary of stock performance.</p>
</div>

</div>

)}

{data && (

<>

{/* AI REPORT */}

<div className="card">

<h2>AI Stock Report</h2>

<p style={{ whiteSpace: "pre-line" }}>
  {data.report}
</p>
<button onClick={downloadPDF} className="downloadBtn">
  Download PDF
</button>
</div>

{/* CHART */}

<div className="chartBox">

<h2>Stock Price Chart</h2>

<ResponsiveContainer width="100%" height={300}>

<LineChart data={chartData}>

<CartesianGrid strokeDasharray="3 3" />

<XAxis dataKey="day" />

<YAxis 
  domain={[
    (dataMin) => dataMin - 5,
    (dataMax) => dataMax + 5
  ]}
/>

<Tooltip />

<Line
type="monotone"
dataKey="price"
stroke="#2563eb"
strokeWidth={3}
/>

</LineChart>

</ResponsiveContainer>

</div>

{/* DASHBOARD */}

<div className="dashboard">

<div className="card">

<h2>Stock Metrics</h2>

<p><b>Ticker:</b> {data.ticker}</p>
<p><b>Price:</b> ${data.price}</p>
<p><b>RSI:</b> {data.indicators?.RSI}</p>
<p><b>Moving Avg (14):</b> {data.indicators?.MA14}</p>
<p><b>Volatility:</b> {data.indicators?.volatility}</p>
<p><b>Signal:</b> {data.signal?.signal}</p>

</div>

<div className="card">

<h2>Market Sentiment</h2>

<p><b>Sentiment:</b> {data.sentiment?.sentiment}</p>
<p><b>Score:</b> {data.sentiment?.score}</p>
<p><b>Articles Analyzed:</b> {data.sentiment?.articles_analyzed}</p>

</div>

</div>

</>

)}

</div>

);

}


export default App;
