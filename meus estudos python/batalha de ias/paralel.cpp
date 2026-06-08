#include <iostream>
#include <string>
#include <sqlite3.h>
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <openssl/crypto.h>
#include <iomanip>
#include <sstream>
#include <ctime>

using namespace std;

const string DB_NAME = "auth.db";
const string PEPPER = "super_secret_pepper";
const int ITERATIONS = 200000;
const int SALT_SIZE = 16;
const int HASH_SIZE = 32;
const int MAX_ATTEMPTS = 5;
const int LOCK_MINUTES = 15;

// ================= UTILS =================
string to_hex(const unsigned char* data, int len) {
    stringstream ss;
    for (int i = 0; i < len; i++)
        ss << hex << setw(2) << setfill('0') << (int)data[i];
    return ss.str();
}

void generate_random(unsigned char* buffer, int size) {
    RAND_bytes(buffer, size);
}

string hash_password(const string& password, unsigned char* salt) {
    unsigned char hash[HASH_SIZE];

    string full = password + PEPPER;

    PKCS5_PBKDF2_HMAC(
        full.c_str(),
        full.length(),
        salt,
        SALT_SIZE,
        ITERATIONS,
        EVP_sha256(),
        HASH_SIZE,
        hash
    );

    return to_hex(hash, HASH_SIZE);
}

bool verify_password(const string& password, string stored_hash, unsigned char* salt) {
    string new_hash = hash_password(password, salt);
    return CRYPTO_memcmp(new_hash.c_str(), stored_hash.c_str(), HASH_SIZE) == 0;
}

// ================= DATABASE =================
sqlite3* db;

void init_db() {
    if (sqlite3_open(DB_NAME.c_str(), &db) != SQLITE_OK) {
        cerr << "Erro ao abrir banco de dados: " << sqlite3_errmsg(db) << "\n";
        sqlite3_close(db);
        exit(1);
    }

    const char* users = R"(
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            salt BLOB,
            attempts INTEGER DEFAULT 0,
            locked_until INTEGER
        );
    )";

    sqlite3_exec(db, users, 0, 0, 0);
}

// ================= REGISTER =================
void register_user(string username, string password) {
    unsigned char salt[SALT_SIZE];
    generate_random(salt, SALT_SIZE);

    string hash = hash_password(password, salt);

    sqlite3_stmt* stmt;
    sqlite3_prepare_v2(db,
        "INSERT INTO users (username, password, salt) VALUES (?, ?, ?)",
        -1, &stmt, 0);

    sqlite3_bind_text(stmt, 1, username.c_str(), -1, SQLITE_STATIC);
    sqlite3_bind_text(stmt, 2, hash.c_str(), -1, SQLITE_STATIC);
    sqlite3_bind_blob(stmt, 3, salt, SALT_SIZE, SQLITE_TRANSIENT);

    if (sqlite3_step(stmt) == SQLITE_DONE)
        cout << "Usuário criado!\n";
    else
        cout << "Erro ao criar usuário\n";

    sqlite3_finalize(stmt);
}

// ================= LOGIN =================
void login(string username, string password) {
    sqlite3_stmt* stmt;

    sqlite3_prepare_v2(db,
        "SELECT id, password, salt, attempts, locked_until FROM users WHERE username=?",
        -1, &stmt, 0);

    sqlite3_bind_text(stmt, 1, username.c_str(), -1, SQLITE_STATIC);

    if (sqlite3_step(stmt) == SQLITE_ROW) {
        int id = sqlite3_column_int(stmt, 0);
        string stored_hash = (char*)sqlite3_column_text(stmt, 1);
        unsigned char* salt = (unsigned char*)sqlite3_column_blob(stmt, 2);
        int attempts = sqlite3_column_int(stmt, 3);
        time_t locked_until = sqlite3_column_int(stmt, 4);

        time_t now = time(0);

        if (locked_until > now) {
            cout << "Conta bloqueada\n";
            return;
        }

        if (verify_password(password, stored_hash, salt)) {
            cout << "Login sucesso!\n";

            sqlite3_exec(db,
                ("UPDATE users SET attempts=0, locked_until=0 WHERE id=" + to_string(id)).c_str(),
                0, 0, 0);
        } else {
            attempts++;

            time_t lock_time = 0;
            if (attempts >= MAX_ATTEMPTS)
                lock_time = now + (LOCK_MINUTES * 60);

            string query = "UPDATE users SET attempts=" + to_string(attempts) +
                           ", locked_until=" + to_string(lock_time) +
                           " WHERE id=" + to_string(id);

            sqlite3_exec(db, query.c_str(), 0, 0, 0);

            cout << "Senha incorreta\n";
        }
    } else {
        cout << "Usuário não encontrado\n";
    }

    sqlite3_finalize(stmt);
}

// ================= MAIN =================
int main() {
    init_db();

    int opcao;
    string user, pass;

    while (true) {
        cout << "\n1. Registrar\n2. Login\n3. Sair\n> ";
        cin >> opcao;

        if (opcao == 1) {
            cout << "Usuário: ";
            cin >> user;
            cout << "Senha: ";
            cin >> pass;
            register_user(user, pass);
        }
        else if (opcao == 2) {
            cout << "Usuário: ";
            cin >> user;
            cout << "Senha: ";
            cin >> pass;
            login(user, pass);
        }
        else break;
    }

    sqlite3_close(db);
    return 0;
}