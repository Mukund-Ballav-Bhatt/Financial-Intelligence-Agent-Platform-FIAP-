import React, { useState } from "react";
import axios from "axios";
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
`http://localhost:8000/report?ticker=${ticker}`
);

setData(response.data);

/* Sample chart data */
const sampleChart = [
{ day: "Mon", price: 100 },
{ day: "Tue", price: 105 },
{ day: "Wed", price: 102 },
{ day: "Thu", price: 108 },
{ day: "Fri", price: 110 }
];

setChartData(sampleChart);

setLoading(false);

} catch (error) {

console.error(error);
alert("Error connecting to backend");
setLoading(false);

}

};

return (

<div className="container">

<header className="header">

<h1>📊 AI Financial Intelligence Platform</h1>

<p>AI powered stock analysis, sentiment detection and market intelligence</p>

</header>

<div className="searchBox">

<input
type="text"
placeholder="Search Stock (AAPL, TSLA, MSFT)"
value={ticker}
onChange={(e) => setTicker(e.target.value)}
/>

<button onClick={analyzeStock}>
{loading ? "Analyzing..." : "Analyze"}
</button>

</div>

{/* Show welcome section before search */}

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

<div className="card">
<h2>AI Summary</h2>
<p>{data.summary}</p>
</div>

<div className="chartBox">

<h2>Stock Price Chart</h2>

<ResponsiveContainer width="100%" height={300}>

<LineChart data={chartData}>

<CartesianGrid strokeDasharray="3 3" />

<XAxis dataKey="day" />

<YAxis />

<Tooltip />

<Line type="monotone" dataKey="price" stroke="#2563eb" strokeWidth={3} />

</LineChart>

</ResponsiveContainer>

</div>

<div className="dashboard">

<div className="card">
<h2>Stock Metrics</h2>
<pre>{JSON.stringify(data.stock_metrics, null, 2)}</pre>
</div>

<div className="card">
<h2>Market Sentiment</h2>
<pre>{JSON.stringify(data.sentiment, null, 2)}</pre>
</div>

</div>

</>

)}

</div>

);

}

export default App;
