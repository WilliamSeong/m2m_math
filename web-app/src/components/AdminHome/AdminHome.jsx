import { useState, useEffect } from "react";

import StudentCard from "./../StudentCard/StudentCard";


const address = "http://192.168.1.141:9050"

export default function AdminHome() {

    const [students, setStudents] = useState([]);

    useEffect(() => {

        async function fetchData() {

            const response = await fetch(`${address}/students`);

            const data = await response.json();

            console.log(data);

            setStudents(data);
        };

    fetchData();

    }, []);

    return(
        <div>
            <h1>Hello</h1>
            {students ? (
                <div>
                    {students.map((student, index) => (
                        <StudentCard key={index} studentInfo={student} />
                    ))}
                </div>
            ) : <p>Loading...</p>}
        </div>
    )
}