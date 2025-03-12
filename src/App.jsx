import { useState, useEffect } from "react";

export default function App() {

  useEffect(() => {

    async function fetchData() {

      const response = await fetch("http://localhost:3000/algebra1");
      
      const data = await response.json();

      console.log(data);
    };


    fetchData();
  })

  return (
    <>
      Hello?
    </>
  )
}