module.exports = {
    entry: [
        './jsx/index.jsx'
    ],
    module: {
        rules: [
            {
                test: /\.jsx$/,
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: ['@babel/preset-react']
                    }
                }
            }
        ]
    },
    output: {
        path: __dirname + '/dist',
        filename: 'bundle.js'
    }
};
