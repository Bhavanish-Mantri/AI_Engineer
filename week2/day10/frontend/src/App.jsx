import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import { 
    Sparkles, Compass, Terminal as TerminalIcon, User, 
    Download, Wifi, Battery, Sliders, ArrowLeft, ArrowRight, 
    RotateCw, Lock, Send, FileText, Folder
} from 'lucide-react';

function App() {
    // 1. Time State (updates every minute)
    const [timeString, setTimeString] = useState('');
    useEffect(() => {
        const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        const months = ['Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'];
        
        const updateClock = () => {
            const now = new Date();
            const day = days[now.getDay()];
            const month = months[now.getMonth()];
            const date = now.getDate();
            let hours = now.getHours();
            let minutes = now.getMinutes();
            const ampm = hours >= 12 ? 'PM' : 'AM';
            
            hours = hours % 12;
            hours = hours ? hours : 12;
            minutes = minutes < 10 ? '0' + minutes : minutes;
            
            setTimeString(`${day}, ${month} ${date}, ${hours}:${minutes} ${ampm}`);
        };
        
        updateClock();
        const interval = setInterval(updateClock, 60000);
        return () => clearInterval(interval);
    }, []);

    // 2. Global Z-Index Counter
    const [maxZIndex, setMaxZIndex] = useState(105);
    const [activeWindowId, setActiveWindowId] = useState('askme');
    const [safariPage, setSafariPage] = useState('projects');

    // 3. Windows Position and Size State
    const [windows, setWindows] = useState({
        askme: {
            isOpen: true,
            isMinimized: false,
            isMaximized: false,
            zIndex: 101,
            position: { x: window.innerWidth > 768 ? Math.round(window.innerWidth * 0.35) : 10, y: 80 },
            size: { width: 420, height: 580 },
            title: 'Ask Me',
            appContext: 'Ask Me'
        },
        resume: {
            isOpen: false,
            isMinimized: false,
            isMaximized: false,
            zIndex: 10,
            position: { x: 80, y: 60 },
            size: { width: 800, height: 600 },
            title: 'Resume.pdf',
            appContext: 'Resume.pdf'
        },
        terminal: {
            isOpen: false,
            isMinimized: false,
            isMaximized: false,
            zIndex: 10,
            position: { x: 120, y: 150 },
            size: { width: 650, height: 420 },
            title: 'bhavanish@portfolio: ~',
            appContext: 'Terminal'
        },
        'rag-assistant': {
            isOpen: false,
            isMinimized: false,
            isMaximized: false,
            zIndex: 10,
            position: { x: 180, y: 120 },
            size: { width: 600, height: 450 },
            title: 'Project: RAG Study Assistant',
            appContext: 'RAG Study Assistant'
        },
        'resume-parser': {
            isOpen: false,
            isMinimized: false,
            isMaximized: false,
            zIndex: 10,
            position: { x: 200, y: 130 },
            size: { width: 600, height: 450 },
            title: 'Project: AI Resume Parser',
            appContext: 'AI Resume Parser'
        },
        'security-trainee': {
            isOpen: false,
            isMinimized: false,
            isMaximized: false,
            zIndex: 10,
            position: { x: 220, y: 140 },
            size: { width: 600, height: 450 },
            title: 'Experience: Cyber Security Trainee',
            appContext: 'Cyber Security'
        },
        'web-dev': {
            isOpen: false,
            isMinimized: false,
            isMaximized: false,
            zIndex: 10,
            position: { x: 240, y: 150 },
            size: { width: 600, height: 450 },
            title: 'Experience: Web Developer Intern',
            appContext: 'Web Dev Internship'
        },
        safari: {
            isOpen: false,
            isMinimized: false,
            isMaximized: false,
            zIndex: 10,
            position: { x: 100, y: 90 },
            size: { width: 800, height: 550 },
            title: 'Safari',
            appContext: 'Safari'
        },
        contact: {
            isOpen: false,
            isMinimized: false,
            isMaximized: false,
            zIndex: 10,
            position: { x: 280, y: 180 },
            size: { width: 450, height: 350 },
            title: 'Contact Info',
            appContext: 'Contacts'
        }
    });

    // Bring clicked window to top
    const focusWindow = (id) => {
        setActiveWindowId(id);
        setWindows(prev => {
            const nextZ = maxZIndex + 1;
            setMaxZIndex(nextZ);
            return {
                ...prev,
                [id]: {
                    ...prev[id],
                    zIndex: nextZ,
                    isMinimized: false // Automatically restore on focus
                }
            };
        });
    };

    // Open/Close Actions
    const openWindow = (id) => {
        setWindows(prev => ({
            ...prev,
            [id]: {
                ...prev[id],
                isOpen: true,
                isMinimized: false
            }
        }));
        focusWindow(id);
    };

    const openSafariPage = (pageName) => {
        setSafariPage(pageName);
        openWindow('safari');
    };

    const closeWindow = (id, e) => {
        if (e) e.stopPropagation();
        setWindows(prev => ({
            ...prev,
            [id]: {
                ...prev[id],
                isOpen: false,
                isMaximized: false
            }
        }));
    };

    const minimizeWindow = (id, e) => {
        if (e) e.stopPropagation();
        setWindows(prev => ({
            ...prev,
            [id]: {
                ...prev[id],
                isMinimized: true
            }
        }));
    };

    const toggleMaximizeWindow = (id, e) => {
        if (e) e.stopPropagation();
        setWindows(prev => ({
            ...prev,
            [id]: {
                ...prev[id],
                isMaximized: !prev[id].isMaximized
            }
        }));
    };

    // DRAG LOGIC (Pointer events handle Desktop & Touch together)
    const handleHeaderPointerDown = (e, id) => {
        // Only left click/primary touches
        if (!e.isPrimary) return;
        focusWindow(id);
        
        const win = windows[id];
        if (win.isMaximized) return;

        const startX = e.clientX;
        const startY = e.clientY;
        const startLeft = win.position.x;
        const startTop = win.position.y;

        const handlePointerMove = (moveEv) => {
            const deltaX = moveEv.clientX - startX;
            const deltaY = moveEv.clientY - startY;
            let newTop = startTop + deltaY;
            let newLeft = startLeft + deltaX;

            if (newTop < 28) newTop = 28; // Keep top below menu bar
            
            setWindows(prev => ({
                ...prev,
                [id]: {
                    ...prev[id],
                    position: { x: newLeft, y: newTop }
                }
            }));
        };

        const handlePointerUp = () => {
            document.removeEventListener('pointermove', handlePointerMove);
            document.removeEventListener('pointerup', handlePointerUp);
        };

        document.addEventListener('pointermove', handlePointerMove);
        document.addEventListener('pointerup', handlePointerUp);
    };

    // 4. ASK ME CHAT STATE & HANDLERS
    const [chatInput, setChatInput] = useState('');
    const [chatMessages, setChatMessages] = useState([
        {
            text: "Hi! I'm Bhavanish's AI assistant. Ask me questions about his skills, experience, projects, or background!",
            sender: 'incoming'
        }
    ]);
    const [isTyping, setIsTyping] = useState(false);
    const chatEndRef = useRef(null);

    useEffect(() => {
        if (chatEndRef.current) {
            chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [chatMessages, isTyping]);

    const sendChatMessage = (textToSend) => {
        const text = textToSend || chatInput.trim();
        if (!text) return;
        
        if (!textToSend) setChatInput('');

        // Append user message
        setChatMessages(prev => [...prev, { text, sender: 'outgoing' }]);
        setIsTyping(true);

        // Fetch response
        fetch('http://127.0.0.1:8000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question: text })
        })
        .then(res => {
            if (!res.ok) throw new Error('API server unavailable');
            return res.json();
        })
        .then(data => {
            setIsTyping(false);
            setChatMessages(prev => [...prev, { text: data.answer, sender: 'incoming' }]);
        })
        .catch(err => {
            setIsTyping(false);
            setChatMessages(prev => [...prev, { 
                text: "I couldn't reach Bhavanish's backend server. Make sure it is running locally by executing 'uv run uvicorn main:app' in the backend folder, and that you have configured your GROQ_API_KEY environment variable!", 
                sender: 'incoming' 
            }]);
        });
    };

    const handleChatSubmit = (e) => {
        if (e.key === 'Enter') {
            sendChatMessage();
        }
    };

    const triggerAskAi = (question) => {
        openWindow('askme');
        sendChatMessage(question);
    };

    // 5. TERMINAL SIMULATOR STATE & HANDLERS
    const [termInput, setTermInput] = useState('');
    const [termHistory, setTermHistory] = useState([
        { text: 'Welcome to Bhavanish OS v1.0.0 (React-powered)', type: 'normal' },
        { text: "Type 'help' to view all available commands.", type: 'normal' },
        { text: '', type: 'normal' }
    ]);
    const termEndRef = useRef(null);

    useEffect(() => {
        if (termEndRef.current) {
            termEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [termHistory]);

    const handleTermSubmit = (e) => {
        if (e.key === 'Enter') {
            const cmd = termInput.trim();
            setTermInput('');
            
            if (!cmd) return;

            setTermHistory(prev => [...prev, { text: `bhavanish@portfolio:~$ ${cmd}`, type: 'prompt' }]);

            const args = cmd.toLowerCase().split(' ');
            const mainCmd = args[0];

            setTimeout(() => {
                let reply = [];
                switch(mainCmd) {
                    case 'help':
                        reply = [
                            { text: 'Available commands:', type: 'normal' },
                            { text: '  about      - Print candidate professional summary', type: 'green' },
                            { text: '  projects   - List generative AI & web projects', type: 'green' },
                            { text: '  skills     - Print technical skills by category', type: 'green' },
                            { text: '  contact    - Print contact info & media profiles', type: 'green' },
                            { text: '  neofetch   - Display OS & LLM engine statistics', type: 'green' },
                            { text: '  clear      - Clear terminal screen', type: 'green' }
                        ];
                        break;
                    case 'about':
                        reply = [
                            { text: 'Professional Summary:', type: 'blue' },
                            { text: 'Computer Science undergraduate (B.Tech CSE, 2027) with hands-on experience building AI applications using Python, LLMs, RAG, and AI Agents. Experienced in developing AI prototypes, integrating APIs, and evaluating AI systems. Strong foundation in software engineering, DSA, and databases, with a keen interest in exploring and applying emerging AI technologies.', type: 'normal' }
                        ];
                        break;
                    case 'projects':
                        reply = [
                            { text: 'Generative AI Projects:', type: 'blue' },
                            { text: '  1. RAG Study Assistant: Streamlit, LangChain, Gemini, HuggingFace', type: 'green' },
                            { text: '     - Semantic querying, parsing, vector embeddings. Evaluated using Ragas metrics.', type: 'normal' },
                            { text: '  2. AI Resume Parser & Evaluator: Python, Groq, Pydantic, Instructor', type: 'green' },
                            { text: '     - JSON schemas extraction and skill gap candidate job-match evaluator.', type: 'normal' }
                        ];
                        break;
                    case 'skills':
                        reply = [
                            { text: 'Technical Skills Matrix:', type: 'blue' },
                            { text: '  - Programming: Python, Java, JavaScript, TypeScript', type: 'yellow' },
                            { text: '  - Generative AI: LLMs, RAG, LangChain, AI Agents, Prompt Engineering, Groq, Gemini, MCP', type: 'yellow' },
                            { text: '  - Evaluation/ML: Ragas metrics, TensorFlow, CNNs, Computer Vision', type: 'yellow' },
                            { text: '  - Application Dev: FastAPI, REST APIs, Streamlit, Pydantic, Instructor, SQL', type: 'yellow' },
                            { text: '  - Tools: Git, GitHub, Linux, Kali Linux, Nmap, Wireshark, Burp Suite', type: 'yellow' }
                        ];
                        break;
                    case 'contact':
                        reply = [
                            { text: 'Contact Information:', type: 'blue' },
                            { text: '  - Email: mantribhavanish@gmail.com', type: 'yellow' },
                            { text: '  - Phone: +91-7877586664', type: 'yellow' },
                            { text: '  - GitHub: github.com/bhavanish-mantri', type: 'yellow' },
                            { text: '  - LinkedIn: linkedin.com/in/bhavanish-mantri', type: 'yellow' }
                        ];
                        break;
                    case 'neofetch':
                        reply = [
                            { text: '        .---.        bhavanish@portfolio', type: 'blue' },
                            { text: '       /     \\       -------------------', type: 'blue' },
                            { text: '       \\.---./       OS: MantriOS v1.0.0 (x86_64)', type: 'blue' },
                            { text: '       /     \\       Host: LLM React Interface', type: 'blue' },
                            { text: '      |  o o  |      Kernel: Groq-Llama-3.3-70b-versatile', type: 'blue' },
                            { text: '       \\  ^  /       Uptime: 6 mins', type: 'blue' },
                            { text: '        \'---\'        Shell: zsh 5.9', type: 'blue' },
                            { text: '                     CPU: Llama 3.3 Versatile 70B', type: 'blue' },
                            { text: '                     RAM: 70 Billion Parameters', type: 'blue' }
                        ];
                        break;
                    case 'clear':
                        setTermHistory([]);
                        return;
                    default:
                        reply = [{ text: `Command not found: '${cmd}'. Type 'help' for instructions.`, type: 'red' }];
                }
                setTermHistory(prev => [...prev, ...reply, { text: '', type: 'normal' }]);
            }, 50);
        }
    };

    // 6. RESUME SHEET NAVIGATION SCROLL LOGIC
    const resumeNavRefs = {
        'summary-sec': useRef(null),
        'skills-sec': useRef(null),
        'experience-sec': useRef(null),
        'projects-sec': useRef(null),
        'education-sec': useRef(null),
        'cert-sec': useRef(null)
    };
    const [activeResumeSec, setActiveResumeSec] = useState('summary-sec');

    const scrollResumeTo = (secId) => {
        setActiveResumeSec(secId);
        const ref = resumeNavRefs[secId];
        if (ref && ref.current) {
            ref.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    };

    // 7. DESKTOP GRID ICONS LIST
    const desktopIcons = [
        { id: 'resume', label: 'Resume.pdf', isPdf: true },
        { id: 'rag-assistant', label: 'RAG Study Assistant' },
        { id: 'resume-parser', label: 'AI Resume Parser' },
        { id: 'security-trainee', label: 'Cyber Security' },
        { id: 'web-dev', label: 'Web Dev Internship' }
    ];

    // Helper to get active classes for window
    const getWindowClassName = (id) => {
        let classes = 'window';
        if (windows[id].isOpen) classes += ' active-window';
        if (activeWindowId === id) classes += ' active-focus';
        if (windows[id].isMinimized) classes += ' minimized';
        if (windows[id].isMaximized) classes += ' maximized';
        return classes;
    };

    return (
        <div className="desktop-environment">
            {/* Top Menu Bar */}
            <header className="menu-bar">
                <div className="menu-left">
                    <span className="menu-item bold">
                        <Sparkles size={14} style={{ fill: 'currentColor' }} />
                    </span>
                    <span className="menu-item bold" id="active-app-name">
                        {windows[activeWindowId]?.appContext || "Bhavanish's Portfolio"}
                    </span>
                    <span className="menu-item" onClick={() => openSafariPage('projects')}>Projects</span>
                    <span className="menu-item" onClick={() => openWindow('contact')}>Contact</span>
                    <span className="menu-item" onClick={() => openWindow('resume')}>Resume</span>
                </div>
                <div className="menu-right">
                    <span className="menu-icon"><Wifi size={15} /></span>
                    <span className="menu-icon"><Battery size={17} /></span>
                    <span className="menu-icon"><Sliders size={14} /></span>
                    <span className="menu-item">{timeString}</span>
                </div>
            </header>

            {/* Desktop Icons Grid */}
            <main className="desktop-grid">
                {desktopIcons.map(icon => (
                    <div 
                        key={icon.id}
                        className="desktop-icon" 
                        tabIndex={0}
                        onDoubleClick={() => openWindow(icon.id)}
                        onTouchEnd={() => openWindow(icon.id)}
                    >
                        <div className="icon-image">
                            {icon.isPdf ? (
                                <svg viewBox="0 0 64 64" width="48" height="48">
                                    <defs>
                                        <linearGradient id="pdfGrad" x1="0" y1="0" x2="1" y2="1">
                                            <stop offset="0%" stop-color="#FF5252"/>
                                            <stop offset="100%" stop-color="#FF1744"/>
                                        </linearGradient>
                                    </defs>
                                    <rect x="10" y="6" width="44" height="52" rx="5" fill="url(#pdfGrad)" />
                                    <path d="M40 6 L54 20 L40 20 Z" fill="#D32F2F" opacity="0.8"/>
                                    <text x="32" y="44" fill="white" fontFamily="'Outfit', sans-serif" fontWeight="bold" fontSize="12" textAnchor="middle">PDF</text>
                                </svg>
                            ) : (
                                <svg viewBox="0 0 64 64" width="48" height="48">
                                    <defs>
                                        <linearGradient id="foldGrad" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="0%" stop-color="#4fc3f7"/>
                                            <stop offset="100%" stop-color="#0288d1"/>
                                        </linearGradient>
                                    </defs>
                                    <path d="M6 10 C6 7.8 7.8 6 10 6 L24 6 L32 14 L54 14 C56.2 14 58 15.8 58 18 L58 54 C58 56.2 56.2 58 54 58 L10 58 C7.8 58 6 56.2 6 54 Z" fill="url(#foldGrad)"/>
                                    <path d="M6 18 L58 18 L54 56 L10 56 Z" fill="#02a8f3" opacity="0.9"/>
                                    <circle cx="32" cy="36" r="8" fill="white" opacity="0.9"/>
                                    {icon.id === 'rag-assistant' ? (
                                        <>
                                            <circle cx="29" cy="35" r="1.5" fill="#0288d1"/>
                                            <circle cx="35" cy="35" r="1.5" fill="#0288d1"/>
                                            <path d="M28 40 Q32 43 36 40" stroke="#0288d1" strokeWidth="1.5" strokeLinecap="round" fill="none"/>
                                        </>
                                    ) : (
                                        <text x="32" y="41" fill="#0288d1" fontFamily="monospace" fontSize="13" fontWeight="bold" textAnchor="middle">&lt;&gt;</text>
                                    )}
                                </svg>
                            )}
                        </div>
                        <span className="icon-label">{icon.label}</span>
                    </div>
                ))}
            </main>

            {/* FLOATING WINDOWS */}

            {/* 1. ASK ME (AI Chat) */}
            <div 
                id="window-askme" 
                className={getWindowClassName('askme')}
                style={{
                    zIndex: windows.askme.zIndex,
                    top: windows.askme.position.y,
                    left: windows.askme.position.x,
                    width: windows.askme.size.width,
                    height: windows.askme.size.height
                }}
            >
                <div className="window-header" onPointerDown={(e) => handleHeaderPointerDown(e, 'askme')}>
                    <div className="window-buttons">
                        <span className="btn-close" onClick={(e) => closeWindow('askme', e)}></span>
                        <span className="btn-minimize" onClick={(e) => minimizeWindow('askme', e)}></span>
                        <span className="btn-maximize" onClick={(e) => toggleMaximizeWindow('askme', e)}></span>
                    </div>
                    <div className="window-title">
                        <Sparkles size={13} />
                        Ask Me
                    </div>
                </div>
                <div className="window-content chat-container">
                    <div className="chat-header">
                        <h3>👋 Ask me anything!</h3>
                    </div>
                    <div className="chat-chips-scroll">
                        <div className="chat-chips">
                            <button className="chip" onClick={() => sendChatMessage('Tell me about yourself')}>Tell me about yourself</button>
                            <button className="chip" onClick={() => sendChatMessage('Projects you made')}>Projects you made</button>
                            <button className="chip" onClick={() => sendChatMessage('Why should I hire you?')}>Why should I hire you?</button>
                            <button className="chip" onClick={() => sendChatMessage('Show your backend skills')}>Show your backend skills</button>
                            <button className="chip" onClick={() => sendChatMessage("What's your tech stack?")}>What's your tech stack?</button>
                        </div>
                    </div>
                    <div className="chat-messages">
                        {chatMessages.map((msg, index) => (
                            <div key={index} className={`message ${msg.sender}`}>
                                <div className="message-bubble" dangerouslySetInnerHTML={{ __html: msg.text.replace(/\n/g, '<br>') }}>
                                </div>
                            </div>
                        ))}
                        {isTyping && (
                            <div className="message incoming">
                                <div className="message-bubble">
                                    <div className="typing-indicator">
                                        <span></span><span></span><span></span>
                                    </div>
                                </div>
                            </div>
                        )}
                        <div ref={chatEndRef} />
                    </div>
                    <div className="chat-input-bar">
                        <input 
                            type="text" 
                            placeholder="Type a message..." 
                            value={chatInput}
                            onChange={(e) => setChatInput(e.target.value)}
                            onKeyDown={handleChatSubmit}
                        />
                        <button className="chat-send-btn" onClick={() => sendChatMessage()}>
                            <Send size={15} />
                        </button>
                    </div>
                </div>
            </div>

            {/* 2. RESUME.PDF VIEW */}
            <div 
                id="window-resume" 
                className={getWindowClassName('resume')}
                style={{
                    zIndex: windows.resume.zIndex,
                    top: windows.resume.position.y,
                    left: windows.resume.position.x,
                    width: windows.resume.size.width,
                    height: windows.resume.size.height
                }}
            >
                <div className="window-header" onPointerDown={(e) => handleHeaderPointerDown(e, 'resume')}>
                    <div className="window-buttons">
                        <span className="btn-close" onClick={(e) => closeWindow('resume', e)}></span>
                        <span className="btn-minimize" onClick={(e) => minimizeWindow('resume', e)}></span>
                        <span className="btn-maximize" onClick={(e) => toggleMaximizeWindow('resume', e)}></span>
                    </div>
                    <div className="window-title">Resume.pdf</div>
                </div>
                <div className="window-content resume-layout">
                    <aside className="resume-sidebar">
                        <ul className="resume-nav">
                            <li className={activeResumeSec === 'summary-sec' ? 'active' : ''} onClick={() => scrollResumeTo('summary-sec')}>Summary</li>
                            <li className={activeResumeSec === 'skills-sec' ? 'active' : ''} onClick={() => scrollResumeTo('skills-sec')}>Technical Skills</li>
                            <li className={activeResumeSec === 'experience-sec' ? 'active' : ''} onClick={() => scrollResumeTo('experience-sec')}>Experience</li>
                            <li className={activeResumeSec === 'projects-sec' ? 'active' : ''} onClick={() => scrollResumeTo('projects-sec')}>Projects</li>
                            <li className={activeResumeSec === 'education-sec' ? 'active' : ''} onClick={() => scrollResumeTo('education-sec')}>Education</li>
                            <li className={activeResumeSec === 'cert-sec' ? 'active' : ''} onClick={() => scrollResumeTo('cert-sec')}>Certifications & Awards</li>
                        </ul>
                        <a href="http://localhost:8000/openapi.json" target="_blank" rel="noreferrer" className="download-btn-wrapper">
                            <button className="resume-download-btn">
                                <Download size={14} />
                                Download Resume
                            </button>
                        </a>
                    </aside>
                    <div className="resume-sheet">
                        <div className="resume-page-header">
                            <h1>Bhavanish Mantri</h1>
                            <h2>AI Software Engineer</h2>
                            <div className="resume-contacts">
                                <span>📞 +91-7877586664</span> | 
                                <span>✉️ mantribhavanish@gmail.com</span> |
                                <span>🔗 <a href="https://linkedin.com" target="_blank" rel="noreferrer">LinkedIn</a></span> |
                                <span>🐙 <a href="https://github.com" target="_blank" rel="noreferrer">GitHub</a></span>
                            </div>
                        </div>

                        <section ref={resumeNavRefs['summary-sec']} id="summary-sec" className="resume-section">
                            <h3>Professional Summary</h3>
                            <p>Computer Science undergraduate (B.Tech CSE, 2027) with hands-on experience building AI applications using Python, LLMs, RAG, and AI Agents. Experienced in developing AI prototypes, integrating APIs, and evaluating AI systems. Strong foundation in software engineering, DSA, and databases, with a keen interest in exploring and applying emerging AI technologies.</p>
                        </section>

                        <section ref={resumeNavRefs['skills-sec']} id="skills-sec" className="resume-section">
                            <h3>Technical Skills</h3>
                            <div className="skills-grid">
                                <div className="skill-category">
                                    <strong>Languages:</strong> Python, Java, JavaScript, TypeScript
                                </div>
                                <div className="skill-category">
                                    <strong>Generative AI:</strong> LLMs, RAG, AI Agents, Prompt Engineering, LangChain, HuggingFace Embeddings, Gemini API, Groq API, MCP
                                </div>
                                <div className="skill-category">
                                    <strong>Evaluation & ML:</strong> Ragas (AI Evaluation), TensorFlow, CNNs, Computer Vision
                                </div>
                                <div className="skill-category">
                                    <strong>App Dev:</strong> FastAPI, REST APIs, Streamlit, Pydantic, Instructor
                                </div>
                                <div className="skill-category">
                                    <strong>Databases & Tools:</strong> SQL, SQLite, Git, GitHub, Linux, VS Code, Postman
                                </div>
                            </div>
                        </section>

                        <section ref={resumeNavRefs['experience-sec']} id="experience-sec" className="resume-section">
                            <h3>Experience</h3>
                            <div className="resume-item">
                                <div className="item-header">
                                    <div>
                                        <strong className="item-title">Web Developer Intern</strong>
                                        <span className="item-subtitle">City Scene Global Pvt. Ltd.</span>
                                    </div>
                                    <span class="item-date">June 2026 – July 2026</span>
                                </div>
                                <ul>
                                    <li>Developed and enhanced full-stack application features using React, JavaScript, and REST APIs while collaborating with developers in an Agile development environment.</li>
                                    <li>Debugged production issues, implemented new features, and maintained existing modules through GitHub pull requests and code reviews.</li>
                                    <li>Performed software testing, issue tracking, and production debugging across multiple application modules.</li>
                                </ul>
                            </div>
                            <div class="resume-item">
                                <div class="item-header">
                                    <div>
                                        <strong class="item-title">Cyber Security Trainee</strong>
                                        <span class="item-subtitle">Learn & Build</span>
                                    </div>
                                    <span class="item-date">May 2025 – July 2025</span>
                                </div>
                                <ul>
                                    <li>Completed hands-on training in Linux, network security, vulnerability assessment, penetration testing, and secure software development.</li>
                                    <li>Used Kali Linux, Nmap, Wireshark, and Burp Suite to analyze network traffic, investigate vulnerabilities, and understand common web application attack vectors.</li>
                                    <li>Strengthened understanding of secure coding, encryption fundamentals, system hardening, and security principles.</li>
                                </ul>
                            </div>
                        </section>

                        <section ref={resumeNavRefs['projects-sec']} id="projects-sec" className="resume-section">
                            <h3>Projects</h3>
                            <div className="resume-item">
                                <div className="item-header">
                                    <strong>RAG Study Assistant</strong>
                                    <span className="item-tech">Python, LangChain, Gemini, Streamlit</span>
                                </div>
                                <ul>
                                    <li>Built a Retrieval-Augmented Generation (RAG) application using LangChain and Gemini for semantic querying of PDF documents.</li>
                                    <li>Implemented document parsing, intelligent text chunking, vector embeddings, retrieval, and prompt engineering to improve response quality.</li>
                                    <li>Evaluated RAG performance using Ragas metrics including Faithfulness, Answer Relevancy, Context Precision, and Recall.</li>
                                </ul>
                            </div>
                            <div className="resume-item">
                                <div className="item-header">
                                    <strong>AI Resume Parser & Resume Evaluator</strong>
                                    <span className="item-tech">Python, Groq, Pydantic, Instructor</span>
                                </div>
                                <ul>
                                    <li>Built an AI-powered application using Large Language Models to extract structured candidate information from PDF and DOCX resumes.</li>
                                    <li>Developed automated pipelines for extracting education, experience, technical skills, certifications, and projects.</li>
                                    <li>Implemented LLM-based candidate evaluation to generate job-match scores, identify skill gaps, and provide AI-assisted recommendations.</li>
                                </ul>
                            </div>
                        </section>

                        <section ref={resumeNavRefs['education-sec']} id="education-sec" className="resume-section">
                            <h3>Education</h3>
                            <div className="resume-item">
                                <div className="item-header">
                                    <div>
                                        <strong>Amity University Rajasthan</strong>
                                        <span className="item-subtitle">B.Tech - Computer Science and Engineering</span>
                                    </div>
                                    <span className="item-date">2023 – 2027</span>
                                </div>
                                <div className="item-extra">CGPA: 8.91 / 10</div>
                            </div>
                        </section>

                        <section ref={resumeNavRefs['cert-sec']} id="cert-sec" className="resume-section">
                            <h3>Certifications & Achievements</h3>
                            <ul>
                                <li><strong>AWS Certified AI Practitioner</strong> – Amazon Web Services (2026)</li>
                                <li><strong>Oracle Cloud Infrastructure Foundations Associate</strong> – Oracle (2026)</li>
                                <li><strong>Full Stack Development</strong> – Simplilearn (2026)</li>
                                <li>Awarded a <strong>25% Merit-Based Academic Scholarship</strong> at Amity University.</li>
                                <li>Solved <strong>100+ Data Structures and Algorithms problems</strong> on LeetCode using Java.</li>
                                <li>Participated in <strong>IDEATHON 6.0 and LNMHACKS Hackathon</strong>, collaborating on AI and software solutions.</li>
                            </ul>
                        </section>
                    </div>
                </div>
            </div>

            {/* 3. TERMINAL WINDOW */}
            <div 
                id="window-terminal" 
                className={getWindowClassName('terminal')}
                style={{
                    zIndex: windows.terminal.zIndex,
                    top: windows.terminal.position.y,
                    left: windows.terminal.position.x,
                    width: windows.terminal.size.width,
                    height: windows.terminal.size.height
                }}
            >
                <div className="window-header" onPointerDown={(e) => handleHeaderPointerDown(e, 'terminal')}>
                    <div className="window-buttons">
                        <span className="btn-close" onClick={(e) => closeWindow('terminal', e)}></span>
                        <span className="btn-minimize" onClick={(e) => minimizeWindow('terminal', e)}></span>
                        <span className="btn-maximize" onClick={(e) => toggleMaximizeWindow('terminal', e)}></span>
                    </div>
                    <div className="window-title">bhavanish@portfolio: ~</div>
                </div>
                <div 
                    className="window-content terminal-content"
                    onClick={() => document.getElementById('term-field')?.focus()}
                >
                    <div className="terminal-history">
                        {termHistory.map((line, idx) => (
                            <p key={idx} className={line.type === 'normal' ? '' : `term-${line.type}`}>
                                {line.text}
                            </p>
                        ))}
                        <div ref={termEndRef} />
                    </div>
                    <div className="terminal-input-line">
                        <span className="terminal-prompt">bhavanish@portfolio:~$</span>
                        <input 
                            id="term-field"
                            type="text" 
                            value={termInput}
                            onChange={(e) => setTermInput(e.target.value)}
                            onKeyDown={handleTermSubmit}
                            autoFocus
                        />
                    </div>
                </div>
            </div>

            {/* 4. RAG STUDY ASSISTANT WINDOW */}
            <div 
                id="window-rag-assistant" 
                className={getWindowClassName('rag-assistant')}
                style={{
                    zIndex: windows['rag-assistant'].zIndex,
                    top: windows['rag-assistant'].position.y,
                    left: windows['rag-assistant'].position.x,
                    width: windows['rag-assistant'].size.width,
                    height: windows['rag-assistant'].size.height
                }}
            >
                <div className="window-header" onPointerDown={(e) => handleHeaderPointerDown(e, 'rag-assistant')}>
                    <div className="window-buttons">
                        <span className="btn-close" onClick={(e) => closeWindow('rag-assistant', e)}></span>
                        <span className="btn-minimize" onClick={(e) => minimizeWindow('rag-assistant', e)}></span>
                        <span className="btn-maximize" onClick={(e) => toggleMaximizeWindow('rag-assistant', e)}></span>
                    </div>
                    <div className="window-title">Project: RAG Study Assistant</div>
                </div>
                <div className="window-content project-detail">
                    <h2>📚 RAG Study Assistant</h2>
                    <p className="proj-subtitle">Semantic querying and QA system for academic PDF documents.</p>
                    <div className="tech-tags">
                        <span>Python</span>
                        <span>LangChain</span>
                        <span>Gemini API</span>
                        <span>HuggingFace Embeddings</span>
                        <span>Streamlit</span>
                        <span>Ragas</span>
                    </div>
                    <h3>Key Features</h3>
                    <ul>
                        <li>Document parsing and ingestion pipeline for raw PDF books and study materials.</li>
                        <li>Intelligent semantic chunking with overlapping margins to maintain narrative context.</li>
                        <li>Local Vector store integration utilizing HuggingFace embeddings for precise vector search.</li>
                        <li>Synthesized, context-aware answers generated via Gemini API, preventing model hallucination.</li>
                        <li>Ragas Evaluation Suite: Audited retrieval accuracy using Faithfulness, Answer Relevancy, and Context Precision.</li>
                    </ul>
                    <div className="action-bar">
                        <button className="proj-action-btn" onClick={() => triggerAskAi('Tell me about your RAG Study Assistant project')}>Ask AI About This Project</button>
                    </div>
                </div>
            </div>

            {/* 5. RESUME PARSER WINDOW */}
            <div 
                id="window-resume-parser" 
                className={getWindowClassName('resume-parser')}
                style={{
                    zIndex: windows['resume-parser'].zIndex,
                    top: windows['resume-parser'].position.y,
                    left: windows['resume-parser'].position.x,
                    width: windows['resume-parser'].size.width,
                    height: windows['resume-parser'].size.height
                }}
            >
                <div className="window-header" onPointerDown={(e) => handleHeaderPointerDown(e, 'resume-parser')}>
                    <div className="window-buttons">
                        <span className="btn-close" onClick={(e) => closeWindow('resume-parser', e)}></span>
                        <span className="btn-minimize" onClick={(e) => minimizeWindow('resume-parser', e)}></span>
                        <span className="btn-maximize" onClick={(e) => toggleMaximizeWindow('resume-parser', e)}></span>
                    </div>
                    <div className="window-title">Project: AI Resume Parser</div>
                </div>
                <div className="window-content project-detail">
                    <h2>📄 AI Resume Parser & Evaluator</h2>
                    <p className="proj-subtitle">Structured JSON extraction and scoring pipeline for job applications.</p>
                    <div className="tech-tags">
                        <span>Python</span>
                        <span>Groq API (Llama 3.3)</span>
                        <span>Pydantic</span>
                        <span>Instructor</span>
                        <span>Prompt Engineering</span>
                    </div>
                    <h3>Key Features</h3>
                    <ul>
                        <li>Structured extraction of candidates' name, contacts, skills, education, and detailed experiences from PDF and Word resumes.</li>
                        <li>Guaranteed schema validation utilizing the Instructor library wrapping Pydantic data schemas.</li>
                        <li>Dynamic skill-gap analysis comparing candidate profiles with specific Job Descriptions (JDs).</li>
                        <li>AI-powered decision matrix scoring candidate match level, providing actionable hiring recommendations.</li>
                    </ul>
                    <div className="action-bar">
                        <button className="proj-action-btn" onClick={() => triggerAskAi('Tell me about your AI Resume Parser project')}>Ask AI About This Project</button>
                    </div>
                </div>
            </div>

            {/* 6. CYBER SECURITY WINDOW */}
            <div 
                id="window-security-trainee" 
                className={getWindowClassName('security-trainee')}
                style={{
                    zIndex: windows['security-trainee'].zIndex,
                    top: windows['security-trainee'].position.y,
                    left: windows['security-trainee'].position.x,
                    width: windows['security-trainee'].size.width,
                    height: windows['security-trainee'].size.height
                }}
            >
                <div className="window-header" onPointerDown={(e) => handleHeaderPointerDown(e, 'security-trainee')}>
                    <div className="window-buttons">
                        <span className="btn-close" onClick={(e) => closeWindow('security-trainee', e)}></span>
                        <span className="btn-minimize" onClick={(e) => minimizeWindow('security-trainee', e)}></span>
                        <span className="btn-maximize" onClick={(e) => toggleMaximizeWindow('security-trainee', e)}></span>
                    </div>
                    <div className="window-title">Experience: Cyber Security Trainee</div>
                </div>
                <div className="window-content project-detail">
                    <h2>🛡️ Cyber Security Trainee @ Learn & Build</h2>
                    <p className="proj-subtitle">Vulnerability assessment, networking protocols, and secure system design.</p>
                    <div className="tech-tags">
                        <span>Linux</span>
                        <span>Kali Linux</span>
                        <span>Nmap</span>
                        <span>Wireshark</span>
                        <span>Burp Suite</span>
                        <span>Security Auditing</span>
                    </div>
                    <h3>Highlights</h3>
                    <ul>
                        <li>Hands-on system administration, network topology modeling, and server hardening on Linux systems.</li>
                        <li>Conducted network security analysis, packet inspection, and vulnerability scans utilizing Nmap and Wireshark.</li>
                        <li>Investigated common web application vulnerabilities (OWASP Top 10) including SQL Injections and XSS using Burp Suite.</li>
                        <li>Studied secure software development practices, encryption techniques, and authentication design.</li>
                    </ul>
                    <div className="action-bar">
                        <button className="proj-action-btn" onClick={() => triggerAskAi('What security skills did you learn during your security training?')}>Ask AI About This</button>
                    </div>
                </div>
            </div>

            {/* 7. WEB DEV INTERN WINDOW */}
            <div 
                id="window-web-dev" 
                className={getWindowClassName('web-dev')}
                style={{
                    zIndex: windows['web-dev'].zIndex,
                    top: windows['web-dev'].position.y,
                    left: windows['web-dev'].position.x,
                    width: windows['web-dev'].size.width,
                    height: windows['web-dev'].size.height
                }}
            >
                <div className="window-header" onPointerDown={(e) => handleHeaderPointerDown(e, 'web-dev')}>
                    <div className="window-buttons">
                        <span className="btn-close" onClick={(e) => closeWindow('web-dev', e)}></span>
                        <span className="btn-minimize" onClick={(e) => minimizeWindow('web-dev', e)}></span>
                        <span className="btn-maximize" onClick={(e) => toggleMaximizeWindow('web-dev', e)}></span>
                    </div>
                    <div className="window-title">Experience: Web Developer Intern</div>
                </div>
                <div className="window-content project-detail">
                    <h2>💻 Web Developer Intern @ City Scene Global</h2>
                    <p className="proj-subtitle">Full-stack feature engineering, REST APIs, and client-side web apps.</p>
                    <div className="tech-tags">
                        <span>React</span>
                        <span>JavaScript</span>
                        <span>REST APIs</span>
                        <span>Agile (Scrum)</span>
                        <span>Git / GitHub</span>
                        <span>Testing & Debugging</span>
                    </div>
                    <h3>Highlights</h3>
                    <ul>
                        <li>Developed and enhanced responsive React client components, interfacing with core backend REST API endpoints.</li>
                        <li>Collaborated in a fast-paced Agile sprint environment, participating in daily standups and sprint reviews.</li>
                        <li>Maintained source code health, debugged live issues, and completed peer code reviews on GitHub.</li>
                        <li>Conducted interface functional tests and resolved cross-browser rendering inconsistencies.</li>
                    </ul>
                    <div className="action-bar">
                        <button className="proj-action-btn" onClick={() => triggerAskAi('Tell me about your Web Developer Internship experience')}>Ask AI About This</button>
                    </div>
                </div>
            </div>

            {/* 8. SAFARI (Web Portfolio Browser) */}
            <div 
                id="window-safari" 
                className={getWindowClassName('safari')}
                style={{
                    zIndex: windows.safari.zIndex,
                    top: windows.safari.position.y,
                    left: windows.safari.position.x,
                    width: windows.safari.size.width,
                    height: windows.safari.size.height
                }}
            >
                <div className="window-header" onPointerDown={(e) => handleHeaderPointerDown(e, 'safari')}>
                    <div className="window-buttons">
                        <span className="btn-close" onClick={(e) => closeWindow('safari', e)}></span>
                        <span className="btn-minimize" onClick={(e) => minimizeWindow('safari', e)}></span>
                        <span className="btn-maximize" onClick={(e) => toggleMaximizeWindow('safari', e)}></span>
                    </div>
                    <div className="window-title">Safari</div>
                </div>
                <div className="window-content browser-layout">
                    <div className="browser-nav-bar">
                        <div className="browser-nav-buttons" style={{ display: 'flex', gap: '10px' }}>
                            <span className="nav-btn" onClick={() => setSafariPage('projects')}>&larr;</span>
                            <span className="nav-btn" onClick={() => setSafariPage('achievements')}>&rarr;</span>
                            <span className="nav-btn">&#8635;</span>
                        </div>
                        <div className="browser-address-bar">
                            <Lock size={11} className="lock-icon" stroke="#00e676" />
                            <span className="address-text">
                                {safariPage === 'projects' ? 'https://bhavanish.dev/projects' : 'https://bhavanish.dev/achievements'}
                            </span>
                        </div>
                    </div>
                    <div className="browser-tabs">
                        <button 
                            className={`browser-tab ${safariPage === 'projects' ? 'active' : ''}`}
                            onClick={() => { setSafariPage('projects'); focusWindow('safari'); }}
                        >
                            📂 Projects
                        </button>
                        <button 
                            className={`browser-tab ${safariPage === 'achievements' ? 'active' : ''}`}
                            onClick={() => { setSafariPage('achievements'); focusWindow('safari'); }}
                        >
                            🏆 Achievements
                        </button>
                    </div>
                    <div className="browser-page-content">
                        {safariPage === 'projects' ? (
                            <>
                                <div className="web-hero">
                                    <h1>Bhavanish's Projects & Prototypes</h1>
                                    <p>A collection of artificial intelligence solutions, agentic systems, and full-stack web applications.</p>
                                </div>
                                <div className="web-cards">
                                    <div className="web-card">
                                        <span className="card-badge">Generative AI / RAG</span>
                                        <h3>RAG Study Assistant</h3>
                                        <p>A smart academic study assistant built using LangChain, Gemini, and Python for PDF semantic querying. Evaluated utilizing Ragas metrics.</p>
                                        <div style={{ marginTop: '14px', display: 'flex', gap: '8px' }}>
                                            <button className="proj-action-btn" style={{ padding: '6px 12px', fontSize: '11.5px' }} onClick={() => triggerAskAi('Tell me about your RAG Study Assistant project')}>Ask AI</button>
                                            <button className="proj-action-btn" style={{ padding: '6px 12px', fontSize: '11.5px', background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.1)', boxShadow: 'none' }} onClick={() => openWindow('rag-assistant')}>Open Folder</button>
                                        </div>
                                    </div>
                                    <div className="web-card">
                                        <span className="card-badge">NLP / Groq</span>
                                        <h3>AI Resume Parser & Evaluator</h3>
                                        <p>An automated pipeline parsing candidate profiles into schemas with Instructor and Llama 3.3. Runs skill-gap evaluation against job descriptions.</p>
                                        <div style={{ marginTop: '14px', display: 'flex', gap: '8px' }}>
                                            <button className="proj-action-btn" style={{ padding: '6px 12px', fontSize: '11.5px' }} onClick={() => triggerAskAi('Tell me about your AI Resume Parser project')}>Ask AI</button>
                                            <button className="proj-action-btn" style={{ padding: '6px 12px', fontSize: '11.5px', background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.1)', boxShadow: 'none' }} onClick={() => openWindow('resume-parser')}>Open Folder</button>
                                        </div>
                                    </div>
                                </div>
                            </>
                        ) : (
                            <>
                                <div className="web-hero">
                                    <h1>Bhavanish's Achievements & Milestones</h1>
                                    <p>A quick overview of major academic and engineering successes.</p>
                                </div>
                                <div className="web-cards">
                                    <div className="web-card">
                                        <span className="card-badge">Scholarship</span>
                                        <h3>25% Merit Scholarship</h3>
                                        <p>Awarded top tier academic scholarship at Amity University Rajasthan for engineering performance.</p>
                                    </div>
                                    <div className="web-card">
                                        <span className="card-badge">DSA</span>
                                        <h3>100+ LeetCode Solved</h3>
                                        <p>Solved a wide array of data structures and algorithms puzzles using Java, focusing on optimization.</p>
                                    </div>
                                    <div className="web-card">
                                        <span className="card-badge">Hackathon</span>
                                        <h3>Hackathon Finalist</h3>
                                        <p>Collaborated and pitched AI prototypes at LNMHACKS and IDEATHON 6.0 conferences.</p>
                                    </div>
                                    <div className="web-card">
                                        <span className="card-badge">Cloud</span>
                                        <h3>AWS & OCI Certified</h3>
                                        <p>AWS Certified AI Practitioner and Oracle Cloud Infrastructure Foundations Associate certifications.</p>
                                    </div>
                                </div>
                            </>
                        )}
                    </div>
                </div>
            </div>

            {/* 9. CONTACT INFO */}
            <div 
                id="window-contact" 
                className={getWindowClassName('contact')}
                style={{
                    zIndex: windows.contact.zIndex,
                    top: windows.contact.position.y,
                    left: windows.contact.position.x,
                    width: windows.contact.size.width,
                    height: windows.contact.size.height
                }}
            >
                <div className="window-header" onPointerDown={(e) => handleHeaderPointerDown(e, 'contact')}>
                    <div className="window-buttons">
                        <span className="btn-close" onClick={(e) => closeWindow('contact', e)}></span>
                        <span className="btn-minimize" onClick={(e) => minimizeWindow('contact', e)}></span>
                        <span className="btn-maximize" onClick={(e) => toggleMaximizeWindow('contact', e)}></span>
                    </div>
                    <div className="window-title">Contact Info</div>
                </div>
                <div className="window-content contact-details">
                    <h2>📬 Let's Connect!</h2>
                    <p>Feel free to reach out for internship opportunities, collaborations, or technical discussions.</p>
                    <div className="contact-links-list">
                        <div className="contact-link-item">
                            <strong>Email:</strong>
                            <a href="mailto:mantribhavanish@gmail.com">mantribhavanish@gmail.com</a>
                        </div>
                        <div className="contact-link-item">
                            <strong>Phone:</strong>
                            <a href="tel:+917877586664">+91 78775 86664</a>
                        </div>
                        <div className="contact-link-item">
                            <strong>GitHub:</strong>
                            <a href="https://github.com" target="_blank" rel="noreferrer">github.com/bhavanish-mantri</a>
                        </div>
                        <div className="contact-link-item">
                            <strong>LinkedIn:</strong>
                            <a href="https://linkedin.com" target="_blank" rel="noreferrer">linkedin.com/in/bhavanish-mantri</a>
                        </div>
                    </div>
                </div>
            </div>

            {/* Bottom macOS Dock */}
            <footer className="dock-container">
                <div className="dock">
                    {/* Finder / Resume */}
                    <div 
                        className={`dock-item ${windows.resume.isOpen ? 'active-running' : ''}`}
                        onClick={() => windows.resume.isOpen ? focusWindow('resume') : openWindow('resume')} 
                        data-label="Finder"
                    >
                        <svg viewBox="0 0 64 64" width="48" height="48">
                            <defs>
                                <linearGradient id="finderGrad" x1="0" y1="0" x2="1" y2="1">
                                    <stop offset="0%" stop-color="#80d8ff"/>
                                    <stop offset="100%" stop-color="#0091ea"/>
                                </linearGradient>
                            </defs>
                            <rect width="60" height="60" x="2" y="2" rx="14" fill="url(#finderGrad)" />
                            <path d="M32 2 C18 2 12 10 12 24 L12 40 C12 54 18 62 32 62 Z" fill="#00b0ff" opacity="0.6"/>
                            <path d="M32 2 L32 62" stroke="#01579b" strokeWidth="2" opacity="0.5"/>
                            <circle cx="21" cy="25" r="3.5" fill="#01579b"/>
                            <circle cx="43" cy="25" r="3.5" fill="#01579b"/>
                            <path d="M19 40 Q32 50 45 40" stroke="#01579b" strokeWidth="3" strokeLinecap="round" fill="none"/>
                            <path d="M32 25 L28 35 L32 35" stroke="#01579b" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
                        </svg>
                        <span className="active-indicator"></span>
                    </div>

                    {/* Safari */}
                    <div 
                        className={`dock-item ${windows.safari.isOpen ? 'active-running' : ''}`}
                        onClick={() => windows.safari.isOpen ? focusWindow('safari') : openSafariPage('projects')} 
                        data-label="Safari"
                    >
                        <svg viewBox="0 0 64 64" width="48" height="48">
                            <defs>
                                <radialGradient id="safGrad" cx="50%" cy="50%" r="50%">
                                    <stop offset="0%" stop-color="#ffffff"/>
                                    <stop offset="50%" stop-color="#e0f7fa"/>
                                    <stop offset="100%" stop-color="#00b0ff"/>
                                </radialGradient>
                            </defs>
                            <circle cx="32" cy="32" r="30" fill="url(#safGrad)" stroke="#0091ea" strokeWidth="1.5" />
                            <circle cx="32" cy="32" r="25" fill="none" stroke="#ffffff" strokeWidth="1" strokeDasharray="2,2"/>
                            <path d="M32 8 L37 27 L32 32 Z" fill="#ff1744"/>
                            <path d="M32 56 L27 37 L32 32 Z" fill="#b0bec5"/>
                            <path d="M32 8 L27 27 L32 32 Z" fill="#d50000"/>
                            <path d="M32 56 L37 37 L32 32 Z" fill="#cfd8dc"/>
                            <circle cx="32" cy="32" r="2.5" fill="#ffffff"/>
                        </svg>
                        <span className="active-indicator"></span>
                    </div>

                    {/* Terminal */}
                    <div 
                        className={`dock-item ${windows.terminal.isOpen ? 'active-running' : ''}`}
                        onClick={() => windows.terminal.isOpen ? focusWindow('terminal') : openWindow('terminal')} 
                        data-label="Terminal"
                    >
                        <svg viewBox="0 0 64 64" width="48" height="48">
                            <rect x="3" y="6" width="58" height="52" rx="10" fill="#263238" />
                            <rect x="3" y="6" width="58" height="52" rx="10" stroke="#37474f" strokeWidth="1.5" fill="none"/>
                            <text x="12" y="34" fill="#00e676" fontFamily="monospace" fontSize="20" fontWeight="bold">&gt;_</text>
                            <rect x="38" y="20" width="10" height="15" fill="#ffffff" opacity="0.8">
                                <animate attributeName="opacity" values="0.8;0;0.8" dur="1s" repeatCount="indefinite" />
                            </rect>
                        </svg>
                        <span className="active-indicator"></span>
                    </div>

                    {/* Contacts */}
                    <div 
                        className={`dock-item ${windows.contact.isOpen ? 'active-running' : ''}`}
                        onClick={() => windows.contact.isOpen ? focusWindow('contact') : openWindow('contact')} 
                        data-label="Contacts"
                    >
                        <svg viewBox="0 0 64 64" width="48" height="48">
                            <defs>
                                <linearGradient id="contGrad" x1="0" y1="0" x2="1" y2="1">
                                    <stop offset="0%" stop-color="#ffb74d"/>
                                    <stop offset="100%" stop-color="#f57c00"/>
                                </linearGradient>
                            </defs>
                            <rect x="4" y="6" width="56" height="52" rx="8" fill="url(#contGrad)" />
                            <rect x="4" y="6" width="6" height="52" rx="2" fill="#e65100" opacity="0.3"/>
                            <circle cx="7" cy="15" r="2.5" fill="#ffffff"/>
                            <circle cx="7" cy="25" r="2.5" fill="#ffffff"/>
                            <circle cx="7" cy="35" r="2.5" fill="#ffffff"/>
                            <circle cx="7" cy="45" r="2.5" fill="#ffffff"/>
                            <circle cx="35" cy="26" r="8" fill="#ffffff"/>
                            <path d="M21 48 C21 40 27 38 35 38 C43 38 49 40 49 48 Z" fill="#ffffff"/>
                        </svg>
                        <span className="active-indicator"></span>
                    </div>

                    <div className="dock-divider"></div>

                    {/* Ask Me Widget */}
                    <div 
                        className={`dock-item ${windows.askme.isOpen ? 'active-running' : ''}`}
                        onClick={() => windows.askme.isOpen ? focusWindow('askme') : openWindow('askme')} 
                        data-label="Ask Me"
                    >
                        <div className="askme-dock-icon">
                            <svg viewBox="0 0 64 64" width="48" height="48">
                                <defs>
                                    <linearGradient id="aiGrad" x1="0" y1="0" x2="1" y2="1">
                                        <stop offset="0%" stop-color="#7c4dff"/>
                                        <stop offset="100%" stop-color="#3f51b5"/>
                                    </linearGradient>
                                </defs>
                                <rect x="2" y="2" width="60" height="60" rx="14" fill="url(#aiGrad)" stroke="rgba(255,255,255,0.2)" strokeWidth="1"/>
                                <path d="M32 14 L35 24 L45 27 L35 30 L32 40 L29 30 L19 27 L29 24 Z" fill="#ffffff"/>
                                <path d="M47 38 L48 43 L53 44 L48 45 L47 50 L46 45 L41 44 L46 43 Z" fill="#80d8ff"/>
                                <path d="M17 12 L17.5 15 L20.5 15.5 L17.5 16 L17 19 L16.5 16 L13.5 15.5 L16.5 15 Z" fill="#e040fb"/>
                            </svg>
                        </div>
                        <span className="active-indicator"></span>
                    </div>
                </div>
            </footer>
        </div>
    );
}

export default App;
