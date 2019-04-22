import React from 'react';
import ReactDOM from 'react-dom';
import io from 'socket.io-client';
import Cookies from 'universal-cookie';

const cookies = new Cookies();

class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            messages: [],
            txtinput: '',
            uname: cookies.get('uname'),
            wsname: cookies.get('wsname'),
            chname: cookies.get('chname'),
        };

        this.post = this.post.bind(this);
        this.inputChange = this.inputChange.bind(this);
    }

    newMsg(m) {
        this.setState({
            messages: this.state.messages.concat(m)
        });
    }

    componentDidMount() {
        const socket = io('http://127.0.0.1:5000');
        this.setState({
            socket: socket
        });

        const wsname = this.state.wsname;
        const chname = this.state.chname;

        socket.emit('join', wsname+':'+chname);

        socket.emit('get msg', wsname, chname, 0, (data) => {
            this.newMsg(data);
        });

        socket.on('new msg', (msg) => {
            console.log(msg);
            this.newMsg(msg);
        });
    }

    componentWillUnmount() {
        const socket = this.state.socket;
        const wsname = this.state.wsname;
        const chname = this.state.chname;

        socket.emit('leave', wsname+':'+chname);
        this.state.socket.close();
    }

    post(event) {
        event.preventDefault();

        if (this.state.txtinput.length == 0) {
            return;
        }

        const m = {
            'sender': this.state.uname,
            'content': this.state.txtinput,
            'wsname': this.state.wsname,
            'chname': this.state.chname
        };

        console.log(m);

        const socket = this.state.socket;

        socket.emit('post msg', m);

        this.setState({
            txtinput: ''
        });
    }

    inputChange(event) {
        this.setState({txtinput: event.target.value});
    }

    render() {
        const messages = this.state.messages;

        const list = messages.map((m) => <li key={m.msgid}>{m.sender}: {m.content}</li>);

        return (
            <div>
                {this.state.uname}
                <form onSubmit={this.post}>
                    <input onChange={this.inputChange} className="form-control" value={this.state.txtinput}/>
                    <button className="btn">Send</button>
                </form>
                {list}
            </div>
        );
    }
}

ReactDOM.render(<App />, document.getElementById('app'));
