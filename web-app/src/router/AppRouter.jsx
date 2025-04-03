import { Routes, Route } from "react-router"

import App from "../App";
import AdminHome from "../components/AdminHome/AdminHome";

import Test from "../components/StudentCard/StudentCard";

export default function AppRouter() {

    return(
        <Routes>
            <Route path="/" element={<App />} />
            <Route path="/admin/home" element={<AdminHome />} />
            <Route path="/test" element={<Test />} />
        </Routes>
    )
}