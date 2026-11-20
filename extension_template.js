const vscode = require('vscode');
const fs = require('fs');
const path = require('path');

function activate(context) {
    context.subscriptions.push(
        vscode.window.registerCustomEditorProvider(
            'umd.editor',
            new UmdEditorProvider(context),
            {
                webviewOptions: { retainContextWhenHidden: true },
                supportsMultipleEditorsPerDocument: false
            }
        )
    );
}

class UmdEditorProvider {
    constructor(context) {
        this.context = context;
        this.htmlTemplate = fs.readFileSync(path.join(__dirname, 'editor.html'), 'utf8');
    }

    async resolveCustomTextEditor(document, webviewPanel, token) {
        webviewPanel.webview.options = {
            enableScripts: true,
        };

        const initialContent = Buffer.from(document.getText(), 'utf8').toString('base64');
        webviewPanel.webview.html = this.htmlTemplate.replace('__INITIAL_CONTENT_BASE64__', initialContent);

        let isInternalEdit = false;
        let lastAppliedText = document.getText();

        function updateWebview() {
            const currentText = document.getText();
            if (currentText === lastAppliedText) {
                return;
            }
            webviewPanel.webview.postMessage({
                type: 'update',
                text: currentText,
                uri: document.uri.toString()
            });
        }

        const changeDocSubscription = vscode.workspace.onDidChangeTextDocument(e => {
            if (e.document.uri.toString() === document.uri.toString()) {
                if (!isInternalEdit) {
                    updateWebview();
                }
            }
        });

        webviewPanel.onDidDispose(() => {
            changeDocSubscription.dispose();
        });

        webviewPanel.webview.onDidReceiveMessage(e => {
            switch (e.type) {
                case 'ready':
                    updateWebview();
                    return;
                case 'edit':
                    lastAppliedText = e.text;
                    isInternalEdit = true;
                    const edit = new vscode.WorkspaceEdit();
                    const fullRange = new vscode.Range(
                        document.positionAt(0),
                        document.positionAt(document.getText().length)
                    );
                    edit.replace(document.uri, fullRange, e.text);
                    vscode.workspace.applyEdit(edit).then(() => {
                        setTimeout(() => {
                            isInternalEdit = false;
                        }, 100);
                    });
                    return;
            }
        });
    }
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};
