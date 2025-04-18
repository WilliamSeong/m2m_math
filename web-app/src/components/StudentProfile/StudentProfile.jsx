import { useParams } from "react-router";
import { useEffect, useState } from "react";
import PDFViewer from "../PDFViewer/PdfViewer";

import "./StudentProfile.css"

const address = "http://192.168.1.103:9050"

export default function StudentProfile() {

    const { studentId } = useParams();
    const [student, setStudent] = useState();
    const [packets, setPackets] = useState();
    const [submissions, setSubmissions] = useState();

    const [levels, setLevels] = useState();
    const [currentObjectives, setCurrentObjectives] = useState([]);
    const [selectedObjectives, setSelectedObjectives] = useState({});

    useEffect( () => {
        const fetchDetails = async () => {

            try {
                const response = await fetch(`${address}/student/details`, {
                    method : "POST",
                    headers : {
                        "Content-Type" : "application/json",
                    },
                    body : JSON.stringify({
                        studentId : studentId
                    })
                });
        
                const data = await response.json();
        
                const { details } = data;

                const resultArray = JSON.parse(details);

                console.log(resultArray);
        
                setStudent(resultArray);
        
            } catch(e) {
                console.log("Student Details fetch error: ", e);
            }
        }

        const fetchPacket = async () => {
            try {
                const response = await fetch(`${address}/student/packets`, {
                    method : "POST",
                    headers : {
                        "Content-Type" : "application/json",
                    },
                    body : JSON.stringify({
                        studentId : studentId
                    })
                });
        
                const data = await response.json();
        
                const { packets } = data;
    
                const packetsArray = JSON.parse(packets);
    
                // console.log(packetsArray);
    
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
                setPackets(urls);
        
            } catch(e) {
                console.log("Student Details fetch error: ", e);
            }
        }

        const fetchSubmissions = async () => {

            try {
                const response = await fetch(`${address}/student/submissions`, {
                    method : "POST",
                    headers : {
                        "Content-Type" : "application/json",
                    },
                    body : JSON.stringify({
                        studentId : studentId
                    })
                });
        
                const data = await response.json();
        
                const { submissions } = data;

                const resultArray = JSON.parse(submissions);

                // console.log(resultArray);
        
                setSubmissions(resultArray);
        
            } catch(e) {
                console.log("Student Details fetch error: ", e);
            }
        }

        const fetchLevels = async () => {
            try {
                const response = await fetch(`${address}/student/levels`, {
                });
        
                const data = await response.json();
        
                const { levels } = data;
    
                const levelsArray = JSON.parse(levels);
    
                // console.log(packetsArray);
    
                setLevels(levelsArray);
        
            } catch(e) {
                console.log("Student Details fetch error: ", e);
            }
        }

        fetchDetails();
        fetchPacket();
        fetchSubmissions();
        fetchLevels()
    }, [studentId])

    function formatDate(isoString) {
        const date = new Date(isoString);
        
        // Force UTC time interpretation
        const month = date.toLocaleString('en-US', { month: 'long', timeZone: 'UTC' });
        const day = date.getUTCDate();
        const year = date.getUTCFullYear();
        
        // Get time components
        const hours = date.getUTCHours();
        const minutes = date.getUTCMinutes();
        const period = hours >= 12 ? 'PM' : 'AM';

        // Convert to 12-hour format
        const formattedHours = hours % 12 || 12;
        
        // Format time with leading zeros for minutes
        const formattedMinutes = minutes.toString().padStart(2, '0');
        
        return `${month} ${day}, ${year} (${formattedHours}:${formattedMinutes} ${period})`;
    }

    async function getLevelObjectives(level){
        console.log(level)
        try {
            const response = await fetch(`${address}/student/level/objectives`, {
                method : "POST",
                headers : {
                    "Content-Type" : "application/json",
                },
                body : JSON.stringify({
                    levelId : level
                })
            });

            const data = await response.json();
    
            const { objectives } = data;

            const objectivesArray = JSON.parse(objectives);

            // console.log(packetsArray);

            setCurrentObjectives(objectivesArray);
    
        } catch(e) {
            console.log("Student Details fetch error: ", e);
        }
    }

    function handleObjectiveSelect(objective) {
        setSelectedObjectives({...selectedObjectives, [objective._id.$oid]: objective});
        console.log(selectedObjectives);
    }

    function handleObjectiveDeselect(objective) {
        // Create a copy of the current state
        const updatedObjectives = { ...selectedObjectives };
        
        // Remove the specific key-value pair
        delete updatedObjectives[objective._id.$oid];
        
        // Update state with the new object
        setSelectedObjectives(updatedObjectives);
    }

    return(
        <div>
            {student && packets && levels ? (
                <div>
                    <div className="student-name">{student.name}</div>
                    <div className="student-id">{student._id.$oid}</div>
                    <div className="student-objectives"> 
                    {Object.entries(student.objectives_inprogress).map(([id, name]) => (
                        <div key={id} className="objective-item">
                            <span className="objective-id">{id}: </span>
                            <span className="objective-name">{name}</span>
                        </div>
                        ))}
                    </div>
                    <div className="pdf-viewer">
                        {packets.map((packetData, index) => (
                            <div key={index}>
                                <PDFViewer url={packetData[0]} count={index}/>
                            </div>
                        ))}
                    </div>
                    <div className="submissions-grid">
                        <div className="submission-header-row">
                            <div className="submission-id">
                                id
                            </div>
                            <div className="submission-score">
                                score
                            </div>
                            <div className="submission-date">
                                date
                            </div>
                        </div>
                        {submissions.slice().reverse().map((submission, index) => (
                            <div key={index} className="submission-row">
                                <div className="submission-id">
                                    {submission._id.$oid}   
                                </div>
                                <div className="submission-score">
                                    {submission.score.correct.length}/{(submission.score.correct.length+submission.score.incorrect.length)}
                                </div>
                                <div className="submission-date">
                                    {formatDate(submission.datetime.$date)}
                                </div>
                            </div>
                        ))}
                    </div>
                    <br/>
                    <div className="objectives-selector">
                        <div className="columns">
                            <div className="levels-label">Levels</div>
                            <div className="levels-content">
                                {levels.map((level, index) => (
                                    <div className="table-item" key={index} onClick={() => getLevelObjectives(level._id.$oid)}>
                                        {level.name}
                                    </div>
                                ))}
                            </div>
                        </div>
                        <div className="columns">
                            <div className="objectives-label">Objectives</div>
                            <div className="objectives-content">
                                {currentObjectives.map((objective, index) => (
                                    objective._id.$oid in student.objectives_inprogress || objective._id.$oid in selectedObjectives ? (
                                        <div className="selected-item" key={index}> {objective.id_number}. {objective.name} </div>
                                    ):(
                                        <div className="table-item" key={index} onClick={() => handleObjectiveSelect(objective)}> {objective.id_number}. {objective.name} </div>
                                    )

                                ))}
                            </div>
                        </div>
                        <div className="columns">
                            <div className="selected-objectives-label">Selected Objectives</div>
                            <div className="selected-objectives-content">
                                {Object.entries(selectedObjectives).map(([id, object]) => (
                                    <div className="table-item" key={id} onClick={() => handleObjectiveDeselect(object)}> {object.id_number}. {object.name} </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            ): (
                <></>
            )}
        </div>
    )
}