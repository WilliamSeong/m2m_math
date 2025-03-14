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
    const [currentStudent, setCurrentStudent] = useState(null);

    useEffect(() => {

        async function fetchData() {

            const response = await fetch("http://localhost:3000/students");

            const data = await response.json();

            console.log(data);

            setStudents(data);
        };

    fetchData();

    }, []);

    async function fetchAllQuestions() {
        const response = await fetch("http://localhost:3000/random5");
            
        const data = await response.json();

        setQuestions(data);

        console.log(data);
    }

    async function handleCurrentStudent(currentStudentId) {
        const response = await fetch("http://localhost:3000/student/details", {
            method : "POST",
            headers : {
                "Content-Type" : "application/json",
            },
            body : JSON.stringify({
                studentId : currentStudentId
            })
    });

        const data = await response.json();

        setCurrentStudent(data);
    }

    return (
        <div>
            {students ? (
                <div>
                    {students.map((student, index) => (
                        <div key={index}>
                            <h1>{student.name}</h1>
                            <p>{student.objectives_inprogress}</p>
                            <button onClick={() => {handleCurrentStudent(student._id)}}>{student.name} details</button>
                        </div>
                    ))}
                </div>
            ) : <p>Loading...</p>}
            {currentStudent ? (
                <h1>{currentStudent.objectives_inprogress}</h1>
            ): (
                <h1></h1>
            )
            }
        </div>
    )
}