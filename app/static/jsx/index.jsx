import React from 'react';
import ReactDOM from 'react-dom';
import io from 'socket.io-client';
import Cookies from 'universal-cookie';
import TimeAgo from 'react-timeago';

const cookies = new Cookies();

class Msg extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            back: '#ffffff',
        };

        this.onMouseEnter = this.onMouseEnter.bind(this);
        this.onMouseLeave = this.onMouseLeave.bind(this);
    }

    onMouseEnter() {
        this.setState({
            back: '#eeeeee',
        });
    }

    onMouseLeave() {
        this.setState({
            back: '#ffffff',
        });
    }

    render () {
        const back = this.state.back;

        const msgStyle = {
            marginTop: '0px',
            marginBottom: '8px',
            padding: '8px',
            background: back,
        }

        const dateStyle = {
            marginLeft: '8px',
        };

        const m = this.props.msg;

        const date = new Date(m.posted);
        const datestr = date.toISOString();


        return (
            <div
                onMouseEnter={this.onMouseEnter}
                onMouseLeave={this.onMouseLeave}
                style={msgStyle}
            >
                <strong>
                    {m.sender}
                </strong>
                <TimeAgo className="text-muted" style={dateStyle} date={datestr} />
                <br />
                {m.content}
            </div>
        );
    }
}

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
        const url = 'http://' + window.location.hostname + ':5000';
        const socket = io(url);
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
        var ch = this.state.chname;
        const uname = this.state.uname;
        var def;

        if (ch[0] == '_') {
            var names = ch.split('_');
            if (names[1] == uname)
                ch = names[2];
            else
                ch = names[1];
            def = "Message " + ch;
        } else {
            def = "Message #" + ch;
        }


        var messages = list.map((m) =>
            <Msg msg={m} key={m.msgid} />
        );

        if (messages.length == 0)
            messages = <h4>Be the first to compose a message!</h4>;

        const formStyle = {
            marginBottom: '10px',
        };

        return (
            <div>
                <form style={formStyle} onSubmit={this.post}>
                    <input placeholder={def} onChange={this.inputChange} className="form-control" value={this.state.txtinput}/>
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
