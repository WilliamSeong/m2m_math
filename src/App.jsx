import { useState, useEffect } from "react";
import Student from "./components/StudentDetails.jsx";


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
    const [students, setStudents] = useState([]);

    useEffect(() => {

        async function fetchData() {

            const response = await fetch("http://localhost:3000/students");

            const data = await response.json();

            console.log(data);
        };

    fetchData();

    })

    async function fetchAllQuestions() {
        const response = await fetch("http://localhost:3000/random5");
            
        const data = await response.json();

        setQuestions(data);

        console.log(data);
    }


    return (
        <div>
            {students ? (
                <div>
                    {students.map((student, index) => (
                        <div key={index}>
                            <h1>Student.name</h1>
                        </div>
                    ))}
                </div>
            ) : <p>Loading...</p>}
            <button onClick={fetchAllQuestions}> Get Questions </button>
            <Student />
        </div>
    )
}