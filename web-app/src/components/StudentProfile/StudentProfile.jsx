import { useParams } from "react-router";
import { useEffect } from "react";

const address = "http://192.168.1.141:9050"

export default function StudentProfile() {

    const { studentId } = useParams();

    useEffect(() => {

        const fetchData = async () => {
            const result = await fetch(`${address}/student/details`)

            const data = json.parse

        }

        fetchData();
    })

    return(
        <div>
            {studentId}
        </div>
    )
}