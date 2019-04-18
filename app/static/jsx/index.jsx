import React from 'react';
import ReactDOM from 'react-dom';

class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            messages: 'have no messages',
            reloads: 0
        };

        this.reload.bind(this);
    }

    componentDidMount() {
        this.interval = setInterval(
            () => this.reload(),
            5000
        );
        this.reload();
    }

    componentWillUnmount() {
        clearInterval(this.interval);
    }

    reload() {
        this.setState({
            reloads: this.state.reloads+1
        });
        const url = window.location.href + '/0';
        console.log(url);
        fetch(url)
            .then(res => res.json())
            .then(
                (json) => {
                    this.setState({
                        messages: json.messages
                    });
                },
                (error) => {
                    this.setState({
                        messages: 'could not get messages'
                    });
                }
            );
    }

    render() {
        return (
            <p>{JSON.stringify(this.state.messages)}</p>
        );
    }
}

ReactDOM.render(<App />, document.getElementById('app'));
