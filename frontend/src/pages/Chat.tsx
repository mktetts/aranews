import axios from 'axios';
import { useState, useRef, useEffect } from 'react';
import { Form, Button, Accordion, Card, Modal } from 'react-bootstrap';
import { FaUser, FaRobot } from 'react-icons/fa';

const Chat = () => {
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState([
        {
            text: "Hello! I'm Chatbot, created by xAI. How can I assist you today?",
            isAI: true,
            timestamp: new Date().toLocaleTimeString()
        }
    ]);
    const [sources, setSources] = useState([]);
    const [graphImage, setGraphImage] = useState("");
    const [query, setQuery] = useState('');
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const [graphPath, setGraphPath] = useState(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSubmit = async (e: any) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage = {
            text: input,
            isAI: false,
            timestamp: new Date().toLocaleTimeString()
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');

        try {
            const response = await fetch('http://127.0.0.1:5000/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: input })
            });

            const data = await response.json();
            console.log(data)
            if (data.aql_query) {
                const aiMessage = {
                    text: data.result,
                    isAI: true,
                    timestamp: new Date().toLocaleTimeString()
                };

                setMessages(prev => [...prev, aiMessage]);
                setSources(data.aql_result || []);
                setQuery(data.aql_query || '');
                // setQuery(data.image);
            }
            else{
                if(data.graph){
                    setGraphPath(data.graph);

                }
                const aiMessage = {
                    text: data.result,
                    isAI: true,
                    timestamp: new Date().toLocaleTimeString()
                };

                setMessages(prev => [...prev, aiMessage]);
                setSources([]);
                setQuery('');
            }
        } catch (error) {
            console.error('Error fetching response:', error);
        }
    };
    const [showModal, setShowModal] = useState(false);
    const [combinedSources, setCombinedSources] = useState('');

    const handleSummarize = () => {
        const allSources = sources.map(source => source.summary_content).join(' ');
        setCombinedSources(allSources);
        setShowModal(true);
    };

    const scheduleContent = async () => {
        const res = await axios.post("http://127.0.0.1:5000/schdule-news", {
            data: combinedSources
        })
        console.log(res)
        if (res.status === 200)
            setShowModal(false);
    }

    return (
        <div
            style={{
                display: 'flex',
                height: '100vh',
                gap: '10px',
                padding: '10px',
                maxHeight: '85vh'
            }}
        >
            {/* Left Sidebar (Sources) */}
            <div
                style={{
                    width: '25%',
                    overflowY: 'auto',
                    backgroundColor: '#f8f9fa',
                    padding: '10px',
                    height: '85vh'
                }}
            >
                <h5>Sources</h5>
                <Accordion>
                    {sources.map((source, index) =>
                        source.summary_content ? (
                            <Accordion.Item key={index} eventKey={index.toString()}>
                                <Accordion.Header>Source {index + 1}</Accordion.Header>
                                <Accordion.Body>
                                    <p>
                                        <strong>Summary:</strong> {source.summary_content}
                                    </p>
                                    <p>
                                        <a href={source.url} target='_blank' rel='noopener noreferrer'>
                                            Read More
                                        </a>
                                    </p>
                                </Accordion.Body>
                            </Accordion.Item>
                        ) : null
                    )}
                </Accordion>

                {sources.length > 0 && (
                    <div
                        className='d-flex align-items-center justify-content-center'
                        style={{
                            position: 'sticky',
                            bottom: '0',
                            background: 'white',
                            padding: '10px',
                            zIndex: '1000',
                        }}
                    >
                        <Button onClick={handleSummarize}>Summarize this</Button>
                    </div>
                )}

            </div>

            {/* Center Chat Area */}
            <div
                style={{
                    flex: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    height: '85vh',
                    maxWidth: '50%'
                }}
            >
                <div className='chat-area' style={{ flex: 1, overflowY: 'auto', padding: '2px' }}>
                {graphPath && (
                <Card
                  style={{
                    width: '100%',
                    marginBottom: '10px',
                    cursor: 'pointer',
                    padding: '10px',
                    boxShadow: '0px 2px 5px rgba(0,0,0,0.2)',
                    textAlign: 'center'
                  }}
                  onClick={() => window.open(graphPath, '_blank')}
                >
                  <p style={{ margin: 0, fontSize: '14px', color: '#007bff' }}>📁 View Graph</p>
                </Card>
              )}
                    {messages.map((message, index) => (
                        <div
                            key={index}
                            style={{
                                marginBottom: '20px',
                                display: 'flex',
                                flexDirection: message.isAI ? 'row' : 'row-reverse',
                                alignItems: 'flex-start'
                            }}
                        >
                            <div
                                style={{
                                    margin: '0 10px',
                                    color: message.isAI ? '#007bff' : '#28a745',
                                    fontSize: '1.2rem'
                                }}
                            >
                                {message.isAI ? <FaRobot /> : <FaUser />}
                            </div>
                            <div
                                style={{
                                    maxWidth: '70%',
                                    padding: '10px 15px',
                                    backgroundColor: message.isAI ? '#e9ecef' : '#d4edda',
                                    borderRadius: '10px',
                                    whiteSpace: 'pre-wrap',
                                    wordBreak: 'break-word'
                                }}
                            >
                                <p style={{ margin: 0 }}>{message.text}</p>
                                <small
                                    style={{
                                        display: 'block',
                                        color: '#666',
                                        marginTop: '5px',
                                        fontSize: '0.8rem'
                                    }}
                                >
                                    {message.timestamp}
                                </small>
                            </div>
                        </div>
                    ))}
                    <div ref={messagesEndRef} />
                </div>

                <div style={{ padding: '20px' }}>
                    <Form onSubmit={handleSubmit}>
                        <div style={{ display: 'flex', gap: '10px' }}>
                            <Form.Control
                                type='text'
                                value={input}
                                onChange={e => setInput(e.target.value)}
                                placeholder='Ask me anything...'
                                style={{
                                    flex: 1,
                                    borderRadius: '20px',
                                    padding: '10px 15px',
                                    border: '1px solid #ced4da'
                                }}
                            />
                            <Button
                                type='submit'
                                style={{
                                    borderRadius: '20px',
                                    padding: '10px 20px',
                                    border: 'none'
                                }}
                            >
                                Send
                            </Button>
                        </div>
                    </Form>
                </div>
            </div>

            {/* Right Sidebar (Query Display) */}
            <div
                style={{
                    width: '25%',
                    overflowY: 'auto',
                    backgroundColor: '#f8f9fa',
                    padding: '10px',
                    height: '85vh'
                }}
            >
                <h5>Executed Query</h5>
                <div
                    style={{
                        backgroundColor: '#fff',
                        padding: '10px',
                        border: '1px solid #ccc',
                        borderRadius: '5px',
                        maxHeight: '80vh',
                        overflowY: 'auto'
                    }}
                >
                    <pre
                        style={{
                            whiteSpace: 'pre-wrap',
                            wordBreak: 'break-word',
                            fontSize: '0.9rem'
                        }}
                    >
                        {query}
                    </pre>
                </div>
            </div>

            <Modal show={showModal} onHide={() => setShowModal(false)} size='lg'>
                <Modal.Header closeButton>
                    <Modal.Title>Schedule</Modal.Title>
                </Modal.Header>
                <Modal.Body style={{
                    maxHeight: '700px',
                    overflowY: 'auto',
                }}><Form.Control
                as="textarea"
                rows={6}
                value={combinedSources}
                onChange={(e) => setCombinedSources(e.target.value)}
                style={{
                  width: '100%',
                  maxHeight: '300px',
                  overflowY: 'auto',
                }}
              /></Modal.Body>
                <Modal.Footer>
                    <Button variant='success' onClick={scheduleContent}>
                        Schedule Content
                    </Button>
                    <Button variant='secondary' onClick={() => setShowModal(false)}>
                        Close
                    </Button>
                </Modal.Footer>
            </Modal>
        </div>
    );
};

export default Chat;
