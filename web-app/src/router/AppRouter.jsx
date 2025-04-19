import { Routes, Route } from "react-router"

import App from "../App";
import AdminHome from "../components/AdminHome/AdminHome";
import StudentProfile from "../components/StudentProfile/StudentProfile";

import Test from "../components/StudentCard/StudentCard";

export default function AppRouter() {

    return(
        <Routes>
            <Route path="/" element={<AdminHome />} />
            {/* <Route path="/admin/home" element={<AdminHome />} /> */}
            <Route path="/student/profile/:studentId" element={<StudentProfile />} />
            <Route path="/test" element={<Test />} />
        </Routes>
    )
}