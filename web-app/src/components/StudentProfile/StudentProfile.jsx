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

    const [objectivesInprogress, setObjectivesInprogress] = useState([]);
    const [levels, setLevels] = useState();
    const [currentObjectives, setCurrentObjectives] = useState([]);
    const [selectedObjectives, setSelectedObjectives] = useState({});

    const [generateObjectives, setGenerateObjectives] = useState({});
    const [generatedPacket, setGeneratedPacket] = useState();

    useEffect( () => {
        const fetchDetails = async () => {

            try {
                const responseDetails = await fetch(`${address}/student/details`, {
                    method : "POST",
                    headers : {
                        "Content-Type" : "application/json",
                    },
                    body : JSON.stringify({
                        studentId : studentId
                    })
                });
        
                const data = await responseDetails.json();
        
                // console.log(data);

                setStudent(data);

                const objective_ids = Object.keys(data.objectives_inprogress)

                const responseObjectives = await fetch(`${address}/student/objectives`, {
                    method : "POST",
                    headers : {
                        "Content-Type" : "application/json",
                    },
                    body : JSON.stringify({
                        objectiveIds : objective_ids
                    })
                });

                const objectives = await responseObjectives.json();

                // console.log(objectives);

                const sortedObjectives = objectives.sort((a, b) => {
                    // First compare by level_id
                    if (a.level_id.$oid !== b.level_id.$oid) {
                      return a.level_id.$oid - b.level_id.$oid; // Sort by level_id first
                    }
                    // If level_id is the same, compare by id_number
                    return a.id_number - b.id_number;
                });
                
                setObjectivesInprogress(sortedObjectives);
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
    
                console.log(packetsArray);
    
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
    
                    urls = [...urls, [packet._id.$oid, url, submissions]];
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
        // console.log(level)
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

            const sortedObjectives = objectivesArray.sort((a, b) => {
                return a.id_number - b.id_number;
            });

            setCurrentObjectives(sortedObjectives);

        } catch(e) {
            console.log("Student Details fetch error: ", e);
        }
    }

    function handleObjectiveSelect(objective) {

        setSelectedObjectives({...selectedObjectives, [objective._id.$oid]: objective});
    }

    function handleObjectiveDeselect(objective) {
        const updatedSelectedObjectives = { ...selectedObjectives };
        delete updatedSelectedObjectives[objective._id.$oid];
        
        setSelectedObjectives(updatedSelectedObjectives);
    }

    async function pushSelectedObjectives(){
        // console.log(selectedObjectives);
        const objectives = Object.keys(selectedObjectives);
        // console.log(objectives);
        try {
            const response = await fetch(`${address}/student/objectives/add`, {
                method : "POST",
                headers : {
                    "Content-Type" : "application/json",
                },
                body : JSON.stringify({
                    objectiveIds : objectives,
                    studentId :student._id.$oid
                })
            });

            const values = Object.values(selectedObjectives)

            console.log("selected objective to add to inprogress: ", values)
            setObjectivesInprogress([...objectivesInprogress, ...values]);
            console.log("new inprogress objective: ", objectivesInprogress);
            setSelectedObjectives({})

        } catch(e) {
            console.log("Objective adding error", e)
        }
    }

    async function completeObjective(objective){
        // console.log(objective)
        if (window.confirm(`Complete objective ${objective.id_number}: \n ${objective.name}`)) {
            try{
                const response = await fetch(`${address}/student/objectives/complete`, {
                    method : "POST",
                    headers : {
                        "Content-Type" : "application/json",
                    },
                    body : JSON.stringify({
                        objectiveId : objective._id.$oid,
                        studentId :student._id.$oid
                    })
                });
            } catch(e) {
                console.log("Objective adding error", e)
            }
        }
    }

    async function incompleteObjective(objective){
        // console.log(objective)
        if (window.confirm(`Mark incomplete objective ${objective.id_number}: \n ${objective.name}`)) {
            try{
                const response = await fetch(`${address}/student/objectives/incomplete`, {
                    method : "POST",
                    headers : {
                        "Content-Type" : "application/json",
                    },
                    body : JSON.stringify({
                        objectiveId : objective._id.$oid,
                        studentId :student._id.$oid
                    })
                });
            } catch(e) {
                console.log("Objective adding error", e)
            }
        }
    }

    function generateObjective(objective){
        setGenerateObjectives({...generateObjectives, [objective._id.$oid] : objective.name})
    }

    function degenerateObjective(objective) {
        const updatedGenerateObjectives = { ...generateObjectives };
        delete updatedGenerateObjectives[objective._id.$oid];
        setGenerateObjectives(updatedGenerateObjectives);
    }

    async function removeInprogressObjectie(objective){
        if (window.confirm(`Remove objective ${objective.id_number}: \n ${objective.name}`)) {
            try{
                const response = await fetch(`${address}/student/objectives/remove`, {
                    method : "POST",
                    headers : {
                        "Content-Type" : "application/json",
                    },
                    body : JSON.stringify({
                        objectiveId : objective._id.$oid,
                        studentId :student._id.$oid
                    })
                });

                // const updatedInprogress = { ...objectivesInprogress };
                // delete updatedInprogress[objective._id.$oid];
                // setObjectivesInprogress(updatedInprogress);        
            } catch(e) {
                console.log("Objective adding error", e)
            }
        }
    }

    async function generatePacket(){

        // console.log(generateObjectives)
        // if (Object.keys(generateObjectives).length != 10) {
        //     window.confirm(`SELECT 10 OBJECTIVES`)
        //     return;
        // }

        const response = await fetch(`${address}/generate`, {
            method : "POST",
            headers : {
                "Content-Type" : "application/json"
            },
            body : JSON.stringify({
                objectiveList : generateObjectives,
                studentId : student._id
            })
        })

        const pdfBlob = await response.blob();
        const pdfUrl = URL.createObjectURL(pdfBlob);
        setGeneratedPacket(pdfUrl);
    }

    return(
        <div>
            {student && objectivesInprogress && levels && submissions ? (
                <div>
                    <div className="student-name">{student.name}</div>
                    <div className="student-id">{student._id.$oid}</div>
                    <div className="student-objectives">
                        {objectivesInprogress.map((objective, index) => (
                            objective._id.$oid in generateObjectives ? (
                            <div key={index} className="selected-objective-item">
                                <div className="objective-name" onClick={() => degenerateObjective(objective)}>{objective.id_number}. {objective.name}</div>
                                <div className="remove-inprogress" onClick={() => removeInprogressObjectie(objective)}>Remove</div>
                                {objective._id.$oid in student.objectives_complete ? (
                                    <div className="objective-complete-button" onClick={() => incompleteObjective(objective)}>Mark Incomplete</div>
                                ): (
                                    <div className="objective-complete-button" onClick={() => completeObjective(objective)}>Mark Complete</div>

                                )}
                            </div>
                            ) : (
                            <div key={index} className="objective-item">
                                <div className="objective-name" onClick={() => generateObjective(objective)}>{objective.id_number}. {objective.name}</div>
                                <div className="remove-inprogress" onClick={() => removeInprogressObjectie(objective)}>Remove</div>
                                {objective._id.$oid in student.objectives_complete ? (
                                    <div className="objective-complete-button" onClick={() => incompleteObjective(objective)}>Mark Incomplete</div>
                                ): (
                                    <div className="objective-complete-button" onClick={() => completeObjective(objective)}>Mark Complete</div>

                                )}
                            </div>
                            )
                        ))}
                    </div>
                    <button onClick={generatePacket}>Generate</button>
                    {generatedPacket ? (
                        <a href={generatedPacket} target="_blank">Packet</a>
                    ) : (
                        <></>
                    )}
                    {packets ? (
                        <div className="pdf-viewer">
                            {packets.map((packetData, index) => (
                                packetData[1] in student.packets_inprogress ? (
                                    <div key={index}>
                                        <PDFViewer studentId={student._id.$oid} packetId={packetData[0]} url={packetData[1]} count={index}/>
                                    </div>
                                ) : (<div key={index}></div>)
                            ))}
                        </div>
                    ): (
                        <></>
                    )}
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
                                    objective._id.$oid in student.objectives_inprogress ? (
                                        objective._id.$oid in student.objectives_complete ? (
                                            <div className="complete-table-item-inprogress" key={index}> {objective.id_number}. {objective.name} </div>
                                        ): (
                                            <div className="selected-item" key={index}> {objective.id_number}. {objective.name} </div>
                                        )
                                    ):(
                                        objective._id.$oid in student.objectives_complete ? (
                                            <div className="complete-table-item" key={index} onClick={() => handleObjectiveSelect(objective)}> {objective.id_number}. {objective.name} </div>
                                        ) : (
                                            objective._id.$oid in selectedObjectives ? (
                                                <div className="selected-item" key={index}> {objective.id_number}. {objective.name} </div>
                                            ) : (
                                                <div className="table-item" key={index} onClick={() => handleObjectiveSelect(objective)}> {objective.id_number}. {objective.name} </div>
                                            )
                                        )
                                    )

                                ))}
                            </div>
                        </div>
                        <div className="columns">
                            <div className="selected-objectives-label">Selected Objectives</div>
                            <div className="selected-objectives-content">
                                {currentObjectives.map((objective, index) => (
                                    objective._id.$oid in selectedObjectives ? (
                                        <div className="table-item" key={index} onClick={() => handleObjectiveDeselect(objective)}> {objective.id_number}. {objective.name} </div>
                                    ) : (<div key={index}></div>)
                                ))}
                            </div>
                        </div>
                    </div>
                    <div>
                        <button onClick={pushSelectedObjectives}>Select</button>
                    </div>
                </div>
            ): (
                <></>
            )}
        </div>
    )
}