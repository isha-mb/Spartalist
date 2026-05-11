#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <unordered_map>
#include <set>
#include <algorithm>
#include <fstream>
#include <sstream>
#include <regex>
#include <ctime>
#include <iomanip>

using namespace std;

const string SCHOOL_NAME      = "Batangas State University TNEU '-' Alangilan Campus";
const string RESULTS_FILENAME = "spartalist_results_2026.txt";
const string ADMIN_PASSWORD   = "admin123";

const vector<string> POSITIONS = {
    "President",
    "Executive Vice President",
    "VP For Student Development & Government - Alangilan",
    "VP For Student Development & Government - Balayan",
};

const map<string, map<string, string>> PARTY_LISTS = {
    {"Habinaya", {
        {"President",                                             "Angel Gionni S. Ornales"},
        {"Executive Vice President",                              "Christopher R. Pacheco"},
        {"VP For Student Development & Government - Alangilan",   "Jose Reyes"},
        {"VP For Student Development & Government - Balayan",     "Ana Villanueva"},
    }},
    {"BatState United", {
        {"President",                                             "Juan dela Cruz"},
        {"Executive Vice President",                              "Liza Bautista"},
        {"VP For Student Development & Government - Alangilan",   "Ryan Fernandez"},
        {"VP For Student Development & Government - Balayan",     "Sophia Ramos"},
    }},
};

// ─────────────────────────────────────────────
//  DATA STRUCTURES USED
// ─────────────────────────────────────────────

struct CandidateNode {
    string name;
    string party;
    string position;
    int    votes;
    CandidateNode* next;

    CandidateNode(const string& n, const string& p, const string& pos)
        : name(n), party(p), position(pos), votes(0), next(nullptr) {}
};

class CandidateLinkedList {
public:
    string position;
    CandidateNode* head;

    CandidateLinkedList() : head(nullptr) {}
    explicit CandidateLinkedList(const string& pos) : position(pos), head(nullptr) {}

    ~CandidateLinkedList() {
        CandidateNode* cur = head;
        while (cur) {
            CandidateNode* tmp = cur->next;
            delete cur;
            cur = tmp;
        }
    }

    void append(const string& name, const string& party) {
        CandidateNode* newNode = new CandidateNode(name, party, position);
        if (!head) {
            head = newNode;
        } else {
            CandidateNode* cur = head;
            while (cur->next) cur = cur->next;
            cur->next = newNode;
        }
    }

    CandidateNode* find(const string& name) const {
        string lower_name = name;
        transform(lower_name.begin(), lower_name.end(), lower_name.begin(), ::tolower);

        CandidateNode* cur = head;
        while (cur) {
            string cur_lower = cur->name;
            transform(cur_lower.begin(), cur_lower.end(), cur_lower.begin(), ::tolower);
            if (cur_lower == lower_name) return cur;
            cur = cur->next;
        }
        return nullptr;
    }

    bool addVote(const string& name) {
        CandidateNode* node = find(name);
        if (node) { node->votes++; return true; }
        return false;
    }

    CandidateNode* getWinner() const {
        CandidateNode* winner = nullptr;
        CandidateNode* cur    = head;
        while (cur) {
            if (!winner || cur->votes > winner->votes)
                winner = cur;
            cur = cur->next;
        }
        return winner;
    }

    vector<CandidateNode*> allCandidates() const {
        vector<CandidateNode*> result;
        CandidateNode* cur = head;
        while (cur) { result.push_back(cur); cur = cur->next; }
        return result;
    }
};

// ─────────────────────────────────────────────
//  VOTING SYSTEM
// ─────────────────────────────────────────────

class VotingSystem {
public:
    unordered_map<string, set<string>> voters;

    map<string, CandidateLinkedList*> ballots;

    VotingSystem()  { buildBallots(); }
    ~VotingSystem() { for (auto& kv : ballots) delete kv.second; }

    void buildBallots() {
        for (const auto& pos : POSITIONS) {
            ballots[pos] = new CandidateLinkedList(pos);
            for (const auto& [party, candidates] : PARTY_LISTS) {
                auto it = candidates.find(pos);
                if (it != candidates.end())
                    ballots[pos]->append(it->second, party);
            }
        }
    }

    bool registerVoter(const string& sid) {
        if (voters.count(sid)) return false;
        voters[sid] = {};
        return true;
    }

    bool isRegistered(const string& sid) const {
        return voters.count(sid) > 0;
    }

    bool hasVotedFor(const string& sid, const string& position) const {
        auto it = voters.find(sid);
        if (it == voters.end()) return false;
        return it->second.count(position) > 0;
    }


    pair<bool, string> castVote(const string& sid, const string& position, const string& candidateName) {
        if (!voters.count(sid))
            return {false, "Student ID not registered. Please register first."};

        if (!ballots.count(position))
            return {false, "'" + position + "' is not a valid position."};

        if (voters[sid].count(position))
            return {false, "You already voted for " + position + "."};

        bool success = ballots[position]->addVote(candidateName);
        if (!success)
            return {false, "Candidate '" + candidateName + "' not found for " + position + "."};

        voters[sid].insert(position);
        return {true, "Vote cast for " + candidateName + " (" + position + ")!"};
    }


    struct PositionResult {
        vector<tuple<string, string, int>> candidates;
        tuple<string, string, int>         winner;
        bool                               hasWinner;
    };

    map<string, PositionResult> getResults() const {
        map<string, PositionResult> results;
        for (const auto& pos : POSITIONS) {
            PositionResult pr;
            pr.hasWinner = false;
            auto* ll = ballots.at(pos);
            for (auto* c : ll->allCandidates())
                pr.candidates.emplace_back(c->name, c->party, c->votes);

            auto* w = ll->getWinner();
            if (w) { pr.winner = {w->name, w->party, w->votes}; pr.hasWinner = true; }
            results[pos] = pr;
        }
        return results;
    }

    int totalVotesCast() const {
        int total = 0;
        for (const auto& [sid, positions] : voters)
            total += (int)positions.size();
        return total;
    }
};

// ─────────────────────────────────────────────
//  HELPERS
// ─────────────────────────────────────────────

VotingSystem* vs = nullptr;

string toUpper(string s) {
    transform(s.begin(), s.end(), s.begin(), ::toupper);
    return s;
}

bool isValidId(const string& sid) {
    regex pattern(R"(^\d{2}-\d{5}$)");
    return regex_match(sid, pattern);
}

string currentDateTime() {
    time_t now = time(nullptr);
    tm* t = localtime(&now);
    char buf[64];
    strftime(buf, sizeof(buf), "%B %d, %Y %I:%M %p", t);
    return string(buf);
}

void clearScreen() {
#ifdef _WIN32
    system("cls");
#else
    system("clear");
#endif
}

void divider(char ch = 0xE2, int width = 58) {
    string line(width, '-');
    if (ch == '=') line = string(width, '=');
    cout << "  " << line << "\n";
}

void dividerEq(int width = 58) { cout << string(width, '=') << "\n"; }
void dividerDash(int width = 58) { cout << "  " << string(width, '-') << "\n"; }
void dividerLine(int width = 58) { cout << string(width, '-') << "\n"; }

void header() {
    clearScreen();
    dividerEq();
    cout << "  SPARTALIST -- " << SCHOOL_NAME << "\n";
    cout << "  Student Council Election System\n";
    dividerEq();
}

// ─────────────────────────────────────────────
//  DISPLAY FUNCTIONS
// ─────────────────────────────────────────────

void showCandidates() {
    cout << "\n  CANDIDATES PER POSITION\n";
    dividerDash();
    for (const auto& pos : POSITIONS) {
        cout << "\n  [" << pos << "]\n";
        for (auto* node : vs->ballots.at(pos)->allCandidates())
            cout << "    * " << left << setw(30) << node->name
                 << " (" << node->party << ")\n";
    }
}

void showLiveResults() {
    header();
    cout << "\n  LIVE LEADERBOARD  |  Total votes cast: "
         << vs->totalVotesCast() << "\n";
    dividerDash();
    auto results = vs->getResults();
    for (const auto& pos : POSITIONS) {
        const auto& data = results[pos];
        cout << "\n  [" << pos << "]\n";

        auto sorted = data.candidates;
        sort(sorted.begin(), sorted.end(),
             [](const auto& a, const auto& b){ return get<2>(a) > get<2>(b); });

        for (const auto& [name, party, votes] : sorted) {
            string bar(votes, '#');
            cout << "    " << left << setw(30) << name
                 << right << setw(3) << votes << " vote(s)  " << bar << "\n";
        }
        if (data.hasWinner && get<2>(data.winner) > 0)
            cout << "    [LEADING] " << get<0>(data.winner)
                 << " (" << get<1>(data.winner) << ")\n";
    }
    dividerDash();
}

void showFinalResults() {
    header();
    cout << "\n  FINAL ELECTION RESULTS\n";
    cout << "  " << SCHOOL_NAME << " -- " << currentDateTime() << "\n";
    dividerEq();

    auto results = vs->getResults();
    vector<string> lines;

    for (const auto& pos : POSITIONS) {
        const auto& data = results[pos];
        string posLine = "\n  POSITION: " + pos;
        string sepLine = "  " + string(40, '-');
        cout << posLine << "\n" << sepLine << "\n";
        lines.push_back(posLine);
        lines.push_back(sepLine);

        auto sorted = data.candidates;
        sort(sorted.begin(), sorted.end(),
             [](const auto& a, const auto& b){ return get<2>(a) > get<2>(b); });

        for (const auto& [name, party, votes] : sorted) {
            bool isWinner = data.hasWinner && name == get<0>(data.winner) && votes > 0;
            string tag = isWinner ? " <- WINNER" : "";
            ostringstream row;
            row << "    " << left << setw(30) << name
                << " (" << party << ")  --  " << votes << " vote(s)" << tag;
            cout << row.str() << "\n";
            lines.push_back(row.str());
        }
    }

    dividerEq();
    cout << "\n  Total registered voters : " << vs->voters.size() << "\n";
    cout << "  Total votes cast        : " << vs->totalVotesCast() << "\n";

    ofstream f(RESULTS_FILENAME);
    if (f.is_open()) {
        f << "SPARTALIST -- " << SCHOOL_NAME << "\n";
        f << "Election Results -- " << currentDateTime() << "\n";
        f << string(58, '=') << "\n";
        for (const auto& l : lines) f << l << "\n";
        f << "\nTotal registered voters : " << vs->voters.size() << "\n";
        f << "Total votes cast        : " << vs->totalVotesCast() << "\n";
        f.close();
        cout << "\n  Results saved to '" << RESULTS_FILENAME << "'\n";
    } else {
        cout << "\n  WARNING: Could not write results file.\n";
    }
}

// ─────────────────────────────────────────────
//  MENUS
// ─────────────────────────────────────────────

void menuRegister() {
    header();
    cout << "\n  VOTER REGISTRATION\n";
    dividerDash();

    while (true) {
        cout << "  Enter Student ID (##-#####): ";
        string sid; getline(cin, sid);

        sid.erase(0, sid.find_first_not_of(" \t\r\n"));
        sid.erase(sid.find_last_not_of(" \t\r\n") + 1);

        if (sid.empty()) {
            cout << "  !!  Student ID cannot be empty.\n";
            cout << "  Press Enter to try again...";
            cin.ignore(); continue;
        }
        if (!isValidId(sid)) {
            cout << "  !!  Invalid format '" << sid
                 << "'. Please use ##-##### (e.g., 25-08323).\n";
            continue;
        }

        string upperSid = toUpper(sid);
        bool ok = vs->registerVoter(upperSid);
        if (ok)
            cout << "  OK  Registered successfully! Welcome, " << upperSid << ".\n";
        else
            cout << "  !!  Student ID " << upperSid << " is already registered.\n";
        break;
    }
    cout << "  Press Enter to continue..."; cin.ignore();
}

void menuVote() {
    header();
    cout << "\n  CAST YOUR VOTE\n";
    dividerDash();

    cout << "  Enter your Student ID (##-#####): ";
    string sid; getline(cin, sid);
    sid.erase(0, sid.find_first_not_of(" \t\r\n"));
    sid.erase(sid.find_last_not_of(" \t\r\n") + 1);

    if (!isValidId(sid)) {
        cout << "  !!  Invalid format. IDs must be ##-#####.\n";
        cout << "  Press Enter to continue..."; cin.ignore(); return;
    }
    sid = toUpper(sid);

    if (!vs->isRegistered(sid)) {
        cout << "  !!  Not registered. Please register first.\n";
        cout << "  Press Enter to continue..."; cin.ignore(); return;
    }

    cout << "\n  Hello, " << sid << "! You may now vote.\n";
    bool votedAny = false;

    for (const auto& position : POSITIONS) {
        if (vs->hasVotedFor(sid, position)) {
            cout << "\n  [" << position << "] -- Already voted. Skipping.\n";
            continue;
        }

        cout << "\n  [" << position << "] -- Choose a candidate:\n";
        auto candidates = vs->ballots.at(position)->allCandidates();
        for (int i = 0; i < (int)candidates.size(); i++)
            cout << "    " << i+1 << ". " << candidates[i]->name
                 << " (" << candidates[i]->party << ")\n";
        cout << "    0. Skip this position\n";

        while (true) {
            cout << "  Your choice (number): ";
            string input; getline(cin, input);

            bool isNum = !input.empty() &&
                         all_of(input.begin(), input.end(), ::isdigit);

            if (input == "0") {
                cout << "  >>  Skipped " << position << ".\n";
                break;
            }
            if (isNum) {
                int choice = stoi(input);
                if (choice >= 1 && choice <= (int)candidates.size()) {
                    auto [ok, msg] = vs->castVote(sid, position, candidates[choice-1]->name);
                    cout << "  " << (ok ? "OK" : "!!") << "  " << msg << "\n";
                    votedAny = true;
                    break;
                }
            }
            cout << "  !!  Invalid choice. Enter 1-"
                 << candidates.size() << " or 0 to skip.\n";
        }
    }

    if (votedAny) cout << "\n  Your votes have been recorded. Thank you!\n";
    cout << "  Press Enter to continue..."; cin.ignore();
}

void menuAdmin() {
    header();
    cout << "\n  ADMIN PANEL\n";
    dividerDash();

    cout << "  Enter admin password: ";
    string pwd; getline(cin, pwd);
    if (pwd != ADMIN_PASSWORD) {
        cout << "  !!  Incorrect password.\n";
        cout << "  Press Enter to continue..."; cin.ignore(); return;
    }

    while (true) {
        header();
        cout << "\n  ADMIN MENU\n";
        dividerDash();
        cout << "  1. View live leaderboard\n";
        cout << "  2. View final results & export\n";
        cout << "  3. View all candidates\n";
        cout << "  4. View registered voters\n";
        cout << "  5. Back to main menu\n";
        dividerDash();
        cout << "  Choose: ";
        string choice; getline(cin, choice);

        if (choice == "1") {
            showLiveResults();
            cout << "\n  Press Enter to continue..."; cin.ignore();
        } else if (choice == "2") {
            showFinalResults();
            cout << "\n  Press Enter to continue..."; cin.ignore();
        } else if (choice == "3") {
            header();
            showCandidates();
            cout << "\n  Press Enter to continue..."; cin.ignore();
        } else if (choice == "4") {
            header();
            cout << "\n  REGISTERED VOTERS (" << vs->voters.size() << " total)\n";
            dividerDash();
            for (const auto& [sid, positions] : vs->voters) {
                string voted = positions.empty() ? "None yet" : "";
                bool first = true;
                for (const auto& p : positions) {
                    if (!first) voted += ", ";
                    voted += p; first = false;
                }
                cout << "  " << left << setw(20) << sid
                     << " Voted for: " << voted << "\n";
            }
            cout << "\n  Press Enter to continue..."; cin.ignore();
        } else if (choice == "5") {
            break;
        }
    }
}

void mainMenu() {
    while (true) {
        header();
        cout << "\n  MAIN MENU\n";
        dividerDash();
        cout << "  1. Register as voter\n";
        cout << "  2. Cast my vote\n";
        cout << "  3. Admin panel\n";
        cout << "  4. Exit\n";
        dividerDash();
        cout << "  Choose: ";
        string choice; getline(cin, choice);

        if      (choice == "1") menuRegister();
        else if (choice == "2") menuVote();
        else if (choice == "3") menuAdmin();
        else if (choice == "4") {
            header();
            cout << "\n  Thank you for using Spartalist!\n";
            cout << "  " << SCHOOL_NAME << " -- Mabuhay ang mga Iskolar!\n\n";
            break;
        } else {
            cout << "  !!  Invalid choice.\n";
            cout << "  Press Enter to continue..."; cin.ignore();
        }
    }
}

// ─────────────────────────────────────────────
//  ENTRY POINT
// ─────────────────────────────────────────────

int main() {
    vs = new VotingSystem();
    mainMenu();
    delete vs;
    return 0;
}
