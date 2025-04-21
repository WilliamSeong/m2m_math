import { useState, useEffect } from "react";

import StudentCard from "./../StudentCard/StudentCard";
import "./AdminHome.css";

const address = "http://192.168.1.103:9050"

export default function AdminHome() {

    const [students, setStudents] = useState([]);

    useEffect(() => {

        async function fetchData() {
            const response = await fetch(`${address}/student/all`);

            const data = await response.json();

            console.log(data);

            setStudents(data);
        };

    fetchData();

    }, []);

    async function testGenerator() {
        const response = await fetch(`${address}/generate/test`);
    }

    async function pdf() {
        const response = await fetch(`${address}/test/pdf`)
    }


    return(
        <div className="admin-home-container">
            <button onClick={pdf}>Test Question</button>
            {students ? (
                <div className="student-cards">
                    {students.map((student, index) => (
                        <StudentCard key={index} studentInfo={student} />
                    ))}
                </div>
            ) : <p>Loading...</p>}
        </div>
    )
}