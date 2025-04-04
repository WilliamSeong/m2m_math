import { useState, useEffect } from "react";
import PDFViewer from "./components/PDFViewer/PdfViewer";


// interface Question{
//     objective : String;
//     level : String;
//     question : String;
//     answer : String[];
//     correct_answer : String
// }

const address = "http://192.168.1.141:9050"

export default function App() {

    // const [question, setQuestion] = useState<Question>(null);
    const [questions, setQuestions] = useState(null);
    const [students, setStudents] = useState([]);
    const [currentStudent, setCurrentStudent] = useState(null);
    const [currentObjectives, setCurrentObjectives] = useState([]);
    const [currentPackets, setCurrentPackets] = useState([]);
    const [testPDF, setTestPDF] = useState([]);

    useEffect(() => {

        async function fetchData() {

            const response = await fetch(`${address}/student/all`);

            const data = await response.json();

            // console.log(data);

            setStudents(data);
        };

    fetchData();

    }, []);

    async function handleCurrentStudent(currentStudentId) {
        try {
            const response = await fetch(`${address}/student/details`, {
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

            const resultArray = JSON.parse(result);
            const packetsArray = JSON.parse(packets);

            // console.log(resultArray);

            let urls = [];
    
            for (const packet of packetsArray ) {
                // console.log("Student id: ", currentStudentId, " packet ", packet);
                const base64Data = packet.content.$binary.base64;
                const binaryString = atob(base64Data);
                
                const bytes = new Uint8Array(binaryString.length);
                for (let i = 0; i < binaryString.length; i++) {
                    bytes[i] = binaryString.charCodeAt(i);
                }
    
                const pdfBlob = new Blob([bytes], { type: 'application/pdf' });
    
                const url = URL.createObjectURL(pdfBlob);

                const submissions = packet.submission_details

                urls = [...urls, [url, submissions]];
            }
            setCurrentStudent(resultArray);
            setCurrentPackets(urls);
    
        } catch(e) {
            console.log("Student Details fetch error: ", e);
        }
    }

    async function handleObjectiveCheckbox() {
        const checkedBoxes = document.querySelectorAll('.objective-checkboxes:checked');
    
        const selectedObjectives = Array.from(checkedBoxes).map(box => {
            const index = parseInt(box.id.split('-')[1]);
            return currentStudent.objectives_inprogress[index];
        });
        
        setCurrentObjectives(selectedObjectives);
        // console.log("Selected objectives:", selectedObjectives);
    }

    async function generateTemplatePacket() {
        // console.log("These are the objectives set for generation: ", currentObjectives);
        const response = await fetch(`${address}/generate`, {
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

    async function testButton() {
        const response = await fetch(`${address}/test/1`)

        const data = await response.json()

        console.log(data)
    }

    async function testButton2() {
        const response = await fetch(`${address}/test/2`)

        const data = await response.json()

        console.log(data)
    }

    async function pdf() {
        const response = await fetch(`${address}/test/pdf`)

        const pdfBlob = await response.blob();
        const data = URL.createObjectURL(pdfBlob);
        
        setTestPDF(data)

        console.log(data)
    }

    return (
        <div>
            {students ? (
                <div>
                    <button onClick={pdf}>Generate PDF with Latex</button>
                    <a href={testPDF} target="_blank">Test PDF</a>
                    {/* <button onClick={testButton2}>Test 2</button> */}
                    {students.map((student, index) => (
                        <div key={index}>
                            <h1>{student.name}</h1>
                            {/* <p>{console.log(student)}</p> */}
                            <button onClick={() => {handleCurrentStudent(student._id)}}>{student.name} details</button>
                        </div>
                    ))}
                </div>
            ) : <p>Loading...</p>}
            {currentStudent ? (
                <div>
                    {currentStudent.objectives_inprogress.map((obj, index) => (
                        <div key={index}>
                            {/* {console.log(obj)} */}
                            <input className="objective-checkboxes" type="checkbox" value={obj} id={`objective-${index}`} onChange={handleObjectiveCheckbox}/>
                            <label htmlFor={`objective-${index}`}>{obj.name}</label>
                        </div>
                    ))}

                    {/* <button onClick={generatePacket}>Generate Packet</button> */}
                    <button onClick={generateTemplatePacket}>Generate Template</button>
                    {questions ? (
                        <a href={questions} target="_blank">Packet</a>
                    ) : (
                        <></>
                    )}
                    {console.log(currentPackets)}
                    {currentPackets.map((packetData, index) => (
                        <div key={index}>
                            <PDFViewer url={packetData[0]} count={index}/>
                            <div>
                                <ul>
                                    {packetData[1].map((submissionData, subIndex) => {
                                        // Extract date and score info
                                        const dateObj = submissionData[0].$date 
                                            ? new Date(submissionData[0].$date) 
                                            : new Date();
                                        
                                        const scoreInfo = submissionData[1];
                                        const total = scoreInfo.correct + scoreInfo.incorrect;
                                        const score = `${scoreInfo.correct}/${total}`;
                                        
                                        const options = { month: 'long', day: 'numeric' };
                                        let dateStr = dateObj.toLocaleDateString('en-US', options);
                                        return (
                                            <li key={subIndex} className="submission-record">
                                                {dateStr}: {score}
                                            </li>
                                        );
                                    })}
                                </ul>
                            </div>
                        </div>
                    ))}
                </div>
            ): (
                <></>
            )}
        </div>
    )
}