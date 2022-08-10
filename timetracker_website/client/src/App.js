import logo from './logo.svg';
import './App.css';
import React, { useEffect, useState } from "react"

function App() {
  const [appState, setAppState] = useState({advice: "", count: 0})

  const fetchData = async () => {
    try {
      const url = "http://localhost:9000/testAPI";
      const testAPI = await fetch(url);
      const text = await testAPI.text();
      console.log(text);
      console.log("hi")
      setAppState({advice: text, count: appState.count})
    } catch (error) {
      console.log("error", error);
    }
  };

  const incrementCounter = () => {
    setAppState({advice: appState.advice, count: appState.count + 1}) 
  }

  useEffect(() => {
    fetchData()
  }, []);


  return (
    <div className="App">
      <header className="App-header">
        <p>
          {appState.count}: {appState.advice}
        </p>
        <button onClick={incrementCounter}>Button</button>
      </header>
    </div>
  );
}

export default App;
