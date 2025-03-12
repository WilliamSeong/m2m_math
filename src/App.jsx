import { useState, useEffect } from "react";

// interface Question{
//     objective : String;
//     level : String;
//     question : String;
//     answer : String[];
//     correct_answer : String
// }

export default function App() {

    // const [question, setQuestion] = useState<Question>(null);
    const [questions, setQuestions] = useState(null);

    useEffect(() => {

    //     async function fetchData() {

    //     const response = await fetch("http://localhost:3000/algebra1");
      
    //     const data = await response.json();

    //     console.log(data);
    // };


    // fetchData();
  })

    async function fetchQuestion() {
        const response = await fetch("http://localhost:3000/algebra1");
            
        const data = await response.json();

        setQuestions(data);

        console.log(data);
    }

    async function fetchAllQuestions() {
        const response = await fetch("http://localhost:3000/all");
            
        const data = await response.json();

        setQuestions(data);

        console.log(data);
    }

    return (
        <div>
            {questions ? (
                <div>
                    {questions.map((question, index) => (
                        <p>
                            {index + 1}. {question.question}
                        </p>
                    ))}
                </div>
            ) : <p>Loading...</p>}
            <button onClick={fetchAllQuestions}> Get Questions </button>
        </div>
    )
}