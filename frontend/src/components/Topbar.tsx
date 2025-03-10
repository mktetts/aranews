import { FiExternalLink } from 'react-icons/fi';
import { IoChatbubbleEllipsesOutline } from 'react-icons/io5';

function TopNavbar() {
    return (
        <nav className='top-navbar'>
            <div className='nav-links'>
                <a href='/main/chat' className='nav-item'>
                    <span>Chat</span> <IoChatbubbleEllipsesOutline />
                </a>
                <a
                    href='http://localhost:8529'
                    target='_blank'
                    rel='noopener noreferrer'
                    className='nav-item'
                >
                    <span>ArangoDB UI</span> <FiExternalLink />
                </a>
                <a
                    href='http://localhost:5678'
                    target='_blank'
                    rel='noopener noreferrer'
                    className='nav-item'
                >
                    <span>n8n UI</span> <FiExternalLink />
                </a>
            </div>
        </nav>
    );
}

export default TopNavbar;
