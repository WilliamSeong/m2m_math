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
    const [currentPackets, setCurrentPackets] = useState([]);
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

        const { result, packets } = data;

        let urls = [];

        for (const packet of packets ) {
            const base64Data = packet.content;
            const binaryString = atob(base64Data);
            
            // Create an array buffer from the binary string
            const bytes = new Uint8Array(binaryString.length);
            for (let i = 0; i < binaryString.length; i++) {
                bytes[i] = binaryString.charCodeAt(i);
            }

            // Create a blob from the array buffer
            const pdfBlob = new Blob([bytes], { type: 'application/pdf' });

            const url = URL.createObjectURL(pdfBlob);
            urls = [...urls, url];
        }
        setCurrentStudent(result);
        setCurrentPackets(urls);
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
                objectiveList : currentObjectives,
                studentId : currentStudent._id,
            })
        })

        const pdfBlob = await response.blob();
        const pdfUrl = URL.createObjectURL(pdfBlob);
        setQuestions(pdfUrl);
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
                        <a href={questions} target="_blank">Packet</a>
                    ) : (
                        <h1></h1>
                    )}

                    {currentPackets.map((url, index) => (
                        <div key={index}><a href={url} target="_blank">Packet {index}</a></div>
                    ))}
                </div>
            ): (
                <h1></h1>
            )}
        </div>
    )
}