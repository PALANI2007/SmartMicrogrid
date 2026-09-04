import ta from '../i18n/ta';

function runTests() {
    let failed = 0;
    
    if (ta.dashboard.title !== 'டாஷ்போர்டு') {
        console.error('Test Failed: Dashboard title is not in Tamil');
        failed++;
    }
    if (ta.settings.title !== 'அமைப்புகள்') {
        console.error('Test Failed: Settings title is not in Tamil');
        failed++;
    }
    if (ta.experiments.title !== 'பரிசோதனைகள்') {
        console.error('Test Failed: Experiments title is not in Tamil');
        failed++;
    }
    
    if (failed === 0) {
        console.log('All i18n tests passed successfully.');
    } else {
        throw new Error('i18n tests failed');
    }
}

runTests();
