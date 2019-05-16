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
            loaded: false,
            more: true,
            uname: cookies.get('uname'),
            wsname: cookies.get('wsname'),
            chname: cookies.get('chname'),
        };

        this.post = this.post.bind(this);
        this.inputChange = this.inputChange.bind(this);
        this.loadMore = this.loadMore.bind(this);
    }

    prependMsg(m) {
        this.setState({
            messages: [].concat(m, this.state.messages),
            loaded: true,
        });
    }

    appendMsg(m) {
        var more = true;
        if (m.length == 0)
            more = false;

        this.setState({
            messages: this.state.messages.concat(m),
            loaded: true,
            more: more,
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
            this.appendMsg(data);
        });

        socket.on('new msg', (msg) => {
            this.prependMsg(msg);
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

    loadMore(event) {
        event.preventDefault();

        const len = this.state.messages.length;
        const socket = this.state.socket;
        const wsname = this.state.wsname;
        const chname = this.state.chname;

        socket.emit('get msg', wsname, chname, len, (data) => {
            this.appendMsg(data);
        });
    }

    render() {
        const list = this.state.messages;

        const msgStyle = {
          marginTop: '10px',
          marginBottom: '10px',
          marginLeft: '5%',
        }

        var messages = list.map((m) =>
            <div className={msgStyle} key={m.msgid}>
                {m.sender}: {m.content}
            </div>
        );

        if (messages.length == 0)
            messages = <h4>Be the first to compose a message!</h4>;

        const formStyle = {
            marginBottom: '10px',
        };

        return (
            <div>
                <form style={formStyle} onSubmit={this.post}>
                    <input onChange={this.inputChange} className="form-control" value={this.state.txtinput}/>
                </form>
                {this.state.loaded ? messages : null}
                {this.state.more
                        ? <a href="#" onClick={this.loadMore}>more</a>
                        : null
                }
            </div>
        );
    }
}

ReactDOM.render(<App />, document.getElementById('app'));
