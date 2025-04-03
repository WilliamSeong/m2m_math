import { createRoot } from 'react-dom/client'
import { BrowserRouter } from "react-router";
import AppRouter from './router/AppRouter.jsx'

createRoot(document.getElementById('root')).render(
    <BrowserRouter>
            <AppRouter />
    </BrowserRouter>
)
