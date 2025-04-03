import { Link } from "react-router";

import "./StudentCard.css";

export default function StudentCard({ studentInfo }) {

    console.log("Student Card Info: ", studentInfo);

    return (
        <div className="student-card-container">
            <div className="card-background">
                <div className="card-name">
                    <Link to={`/student/profile/${studentInfo._id}`}>{studentInfo.name}</Link>
                </div>
                <div className="card-field-first">
                    Grade: {studentInfo.grade}
                </div>
                <div className="card-field-second">
                    Objectives: {studentInfo.objectives_inprogress.length}
                </div>
                <div className="card-field-third">
                    Packets: {studentInfo.packets_inprogress.length}
                </div>
                <div className="card-field-last">
                    Later
                </div>
            </div>
        </div>
    )
}