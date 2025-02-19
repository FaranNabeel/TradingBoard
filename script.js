document.addEventListener('DOMContentLoaded', () => {
    const wsStatus = document.getElementById('ws-status');
    const wsStatusText = wsStatus.querySelector('span:last-child');
    const wsStatusDot = wsStatus.querySelector('.dot');

    let ws;
    let masterAccount = null;
    let clientSockets = [];

   // Function to establish WebSocket connection
   function connectWebSocket() {
    ws = new WebSocket('ws://localhost:8080'); // Connect to your WebSocket server

    ws.onopen = () => {
        console.log('Connected to WebSocket server');
        wsStatusText.textContent = 'WebSocket Status: Connected';
        wsStatusDot.style.backgroundColor = 'green';

        if (masterAccount) {
            ws.send(JSON.stringify({ type: 'connect', role: 'master', apiKey: masterAccount.apiKey }));
        }

        const clientAccounts = JSON.parse(sessionStorage.getItem('clientAccounts')) || [];
        clientAccounts.forEach(account => {
            ws.send(JSON.stringify({ type: 'connect', role: 'client', apiKey: account.apiKey }));
        });

        fetchAllBalances();
    };

    ws.onclose = () => {
        console.log('WebSocket connection closed');
        wsStatusText.textContent = 'WebSocket Status: Not Connected';
        wsStatusDot.style.backgroundColor = 'red';
        setTimeout(connectWebSocket, 1000);
    };

    ws.onerror = (error) => {
        console.log('WebSocket Error:', error);
        wsStatusText.textContent = 'WebSocket Status: Error';
        wsStatusDot.style.backgroundColor = 'orange';
    };

    ws.onmessage = (message) => {
        try {
            const data = JSON.parse(message.data);

            if (data.type === 'balanceUpdate' && data.apiKey) {
                updateAccountBalance(data.apiKey, data.balance);
            }

            if (data.type === 'statusUpdate') {
                updateAccountStatus(data.apiKey, data.status);
            }
        } catch (error) {
            console.error('Error processing WebSocket message:', error);
        }
    };
}


    // Update account status based on WebSocket connection
    function updateAccountStatus(apiKey, status) {
        const statusElement = document.getElementById(`status-${apiKey}`);
        if (statusElement) {
            statusElement.textContent = `Status: ${status.charAt(0).toUpperCase() + status.slice(1)}`;
            statusElement.classList.remove('not-connected', 'connected');
            statusElement.classList.add(status);
        }
    }

    // Handle "Execute" button click to trigger WebSocket connection if both master and client accounts are added
    const executeButton = document.getElementById('executeButton');
    executeButton.addEventListener('click', function() {
        if (masterAccount && document.querySelectorAll('.client-account').length > 0) {
            // Fetch and replicate the active trades from master to clients
            // Establish WebSocket connection only if both master and client accounts are added
            if (!ws || ws.readyState !== WebSocket.OPEN) {
                connectWebSocket();
            }
        } else {
            alert('Both master and client accounts must be added first!');
        }
    });


    const masterForm = document.getElementById('master-form');
    const clientForm = document.getElementById('client-form');
    const masterAccountList = document.getElementById('master-account-list');
    const clientAccountsList = document.getElementById('client-accounts-list');
    
    // Flag for master account
    let masterAccountAdded = false;
    let clientAccountAdded = false;

    // Function to check if "Execute" button should be enabled
    function checkExecuteButton() {
        if (masterAccountList.children.length > 0 && clientAccountsList.children.length > 0) {
            executeButton.disabled = false;
        } else {
            executeButton.disabled = true;
        }
    }

    // Initial check to disable the execute button
    checkExecuteButton();

    masterForm.addEventListener('submit', function(event) {
        event.preventDefault();
    
        const accountName = document.getElementById('masterAccountName').value.trim();
        const apiKey = document.getElementById('masterApiKey').value.trim();
        const secretKey = document.getElementById('masterSecretKey').value.trim();
        const passphrase = document.getElementById('masterPassphrase').value.trim();
    
        if (!accountName || !apiKey || !secretKey || !passphrase) {
            alert('All fields are required for the master account.');
            return;
        }
    
        if (masterAccount) {
            alert('Master account has already been added.');
            return;
        }
    
        sessionStorage.setItem('masterAccount', JSON.stringify({ accountName, apiKey, secretKey, passphrase }));
        masterAccount = { accountName, apiKey, secretKey, passphrase };
        addAccountToList('master', accountName, apiKey, secretKey, passphrase);
        checkExecuteButton();
    
        // Clear the form fields after successful submission
        masterForm.reset();
    });

    clientForm.addEventListener('submit', function(event) {
        event.preventDefault();
    
        const accountName = document.getElementById('clientAccountName').value.trim();
        const apiKey = document.getElementById('clientApiKey').value.trim();
        const secretKey = document.getElementById('clientSecretKey').value.trim();
        const passphrase = document.getElementById('clientPassphrase').value.trim();
    
        if (!accountName || !apiKey || !secretKey || !passphrase) {
            alert('All fields are required for the client account.');
            return;
        }
    
        const clientAccount = { accountName, apiKey, secretKey, passphrase };
        let clientAccounts = JSON.parse(sessionStorage.getItem('clientAccounts')) || [];
        clientAccounts.push(clientAccount);
        sessionStorage.setItem('clientAccounts', JSON.stringify(clientAccounts));
    
        addAccountToList('client', accountName, apiKey, secretKey, passphrase);
        checkExecuteButton();
    
        // Clear the form fields after successful submission
        clientForm.reset();
    });

    // Adds account to the list
    function addAccountToList(type, accountName, apiKey, secretKey, passphrase) {
        if (!accountName) {
            return; // Do not add the account if the account name is not provided
        }

        const accountItem = document.createElement('li');
        accountItem.className = 'list-group-item d-flex justify-content-between align-items-center account-item';

        accountItem.innerHTML = `
            <div class="account-details">
                <strong>Account Name:</strong> ${accountName}
                <div class="status not-connected" id="status-${apiKey}">Status: Not Connected</div>
                <div class="balance" id="balance-${apiKey}">Balance: Fetching...</div>
                <div class="status-message">Waiting for execution...</div>
            </div>
            <div>
                <button class="btn btn-sm btn-danger btn-delete" onclick="deleteAccount(this)">Delete</button>
            </div>
        `;

        accountItem.setAttribute('data-apiKey', apiKey);
        accountItem.setAttribute('data-secretKey', secretKey);
        accountItem.setAttribute('data-passphrase', passphrase);

        if (type === 'master') {
            masterAccountList.appendChild(accountItem);
        } else {
            clientAccountsList.appendChild(accountItem);
        }
    }

    window.deleteAccount = function (button) {
        const accountItem = button.closest('.account-item');
        const apiKey = accountItem.getAttribute('data-apiKey');
        const type = accountItem.parentNode.id === 'master-account-list' ? 'master' : 'client';
    
        // Remove from sessionStorage and DOM
        if (type === 'master') {
            sessionStorage.removeItem('masterAccount');
            masterAccount = null; // Allow adding a new master account
            masterAccountList.removeChild(accountItem);
    
            // Reset the master account form
            masterForm.reset();

             // Remove the "Master account has been added!" message
    const masterMessage = document.getElementById('masterMessage');
    if (masterMessage) {
        masterMessage.textContent = ''; // Clear the message
    }


    // Enable the "Add Master Account" button
const masterSubmit = document.getElementById('masterSubmit');
if (masterSubmit) {
    masterSubmit.disabled = false; // Re-enable the button
}


}
    else {
            let clientAccounts = JSON.parse(sessionStorage.getItem('clientAccounts')) || [];
            clientAccounts = clientAccounts.filter(account => account.apiKey !== apiKey);
            sessionStorage.setItem('clientAccounts', JSON.stringify(clientAccounts));
            clientAccountsList.removeChild(accountItem);
    
            alert('Client account removed.');
    
            // Re-enable the "Execute" button check
            checkExecuteButton();
    }
        };
    
    // Fetch and display accounts from sessionStorage
    window.onload = function() {
        const storedMasterAccount = sessionStorage.getItem('masterAccount');
        const storedClientAccounts = sessionStorage.getItem('clientAccounts');

        if (storedMasterAccount) {
            const { accountName, apiKey, secretKey, passphrase } = JSON.parse(storedMasterAccount);
            masterAccount = { accountName, apiKey, secretKey, passphrase };
            addAccountToList('master', accountName, apiKey, secretKey, passphrase);
        }

        if (storedClientAccounts) {
            const clientAccounts = JSON.parse(storedClientAccounts);
            clientAccounts.forEach(account => {
                addAccountToList('client', account.accountName, account.apiKey, account.secretKey, account.passphrase);
            });
        }

        checkExecuteButton();
    };
});
