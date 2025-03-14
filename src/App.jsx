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
    const [currentObjectives, setCurrentObjectives] = useState([]);
    const [pdfUrls, setPdfUrls] = useState();

    useEffect(() => {

        async function fetchData() {

            const response = await fetch("http://localhost:3000/students");

            const data = await response.json();

            // console.log(data);

            setStudents(data);
        };

    fetchData();

    }, []);

    // async function fetchAllQuestions() {
    //     const response = await fetch("http://localhost:3000/random5");
            
    //     const data = await response.json();

    //     setQuestions(data);

    //     console.log(data);
    // }

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

    async function handleObjectiveCheckbox() {
        const checkedBoxes = document.querySelectorAll('.objective-checkboxes:checked');
    
        const selectedObjectives = Array.from(checkedBoxes).map(box => box.value);
        
        setCurrentObjectives(selectedObjectives);
        console.log("Selected objectives:", selectedObjectives);
    }

    async function generatePacket() {

        console.log("These are the objectives set for generation: ", currentObjectives);
        const response = await fetch("http://localhost:3000/generate", {
            method : "POST",
            headers : {
                "Content-Type" : "application/json"
            },
            body : JSON.stringify({
                objectiveList : currentObjectives
            })
        })

        const data = await response.json();
        const shuffled = data.sort(() => 0.5 - Math.random());
        setQuestions(shuffled);
    }

    async function testPDF() {
        console.log("Testing pdf");

        const response = await fetch("http://localhost:3000/pdf");

        const pdfBlob = await response.blob();

        const pdfUrl = URL.createObjectURL(pdfBlob);

        setPdfUrls(pdfUrl);
    }

    return (
        <div>
            {students ? (
                <div>
                    {students.map((student, index) => (
                        <div key={index}>
                            <h1>{student.name}</h1>
                            {/* <p>{student.objectives_inprogress}</p> */}
                            <button onClick={() => {handleCurrentStudent(student._id)}}>{student.name} details</button>
                        </div>
                    ))}
                </div>
            ) : <p>Loading...</p>}
            {currentStudent ? (
                <div>
                    {currentStudent.objectives_inprogress.map((obj, index) => (
                        <div key={index}>
                            <input className="objective-checkboxes" type="checkbox" value={obj} id={`objective-${index}`} onChange={handleObjectiveCheckbox}/>
                            <label htmlFor={`objective-${index}`}>{obj}</label>
                        </div>
                    ))}

                    <button onClick={generatePacket}>Generate Packet</button>
                    {questions ? (
                        <div>
                            {questions.map((question, index) => (
                                <div key={index}>
                                    <h1>{question.question}</h1>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <h1></h1>
                    )}
                </div>
            ): (
                <h1></h1>
            )}
            <button onClick={testPDF}>Test PDF</button>
            {pdfUrls ? (<a href={pdfUrls} target="_blank">test link</a>) : (<h1></h1>)}
        </div>
    )
}