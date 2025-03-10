import { Route, Routes } from 'react-router-dom';
import TopNavbar from '../components/Topbar';
import Chat from './Chat';

function Main() {
    return (
        <div>
            <TopNavbar />
            <div
                style={{
                    paddingLeft: '40px',
                    paddingRight: '40px',
                    paddingBottom: '10px',
                    paddingTop: '80px'
                }}
            >
                <Routes>
                    <Route path='/chat' element={<Chat />} />
                </Routes>
            </div>
        </div>
    );
}

export default Main;
