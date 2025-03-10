import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import Init from './pages/Init';
import Main from './pages/Main';

function App() {
    return (
        <div>
            <Router>
                <Routes>
                    <Route path='/' element={<Init />} />
                    <Route path='/main/*' element={<Main />} />
                </Routes>
            </Router>
        </div>
    );
}

export default App;
